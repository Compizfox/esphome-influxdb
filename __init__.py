import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.const import CONF_ID, CONF_USERNAME, CONF_PASSWORD, CONF_SENSORS
from esphome.core import coroutine_with_priority
from esphome.core import CORE

DEPENDENCIES = ['network']
AUTO_LOAD = ['http_request']

influxdb_ns = cg.esphome_ns.namespace('influxdb')
InfluxDBWriter = influxdb_ns.class_('InfluxDBWriter', cg.Component, cg.Controller)

CONF_SERVER = 'server'
CONF_DATABASE = 'database'
CONF_SEND_TIMEOUT = 'send_timeout'
CONF_TAGS = 'tags'
CONF_PUBLISH_ALL = 'publish_all'
CONF_IGNORE = 'ignore'
CONF_MEASUREMENT = 'measurement'
CONF_FIELD = 'field'


SENSOR_SCHEMA = cv.Schema({
   cv.validate_id_name:
       cv.Schema({
       cv.Optional(CONF_IGNORE, default=False): cv.boolean,
       cv.Optional(CONF_FIELD): cv.string,
       cv.Optional(CONF_TAGS, default={}): cv.Schema({
           cv.string: cv.string
       })
   })
})

CONFIG_SCHEMA = cv.Schema({
    cv.GenerateID(): cv.declare_id(InfluxDBWriter),
    cv.Required(CONF_SERVER): cv.url,
    cv.Optional(CONF_USERNAME, default=''): cv.string_strict,
    cv.Optional(CONF_PASSWORD, default=''): cv.string_strict,
    cv.Required(CONF_DATABASE): cv.string_strict,
    cv.Required(CONF_MEASUREMENT): cv.string_strict,
    cv.Optional(CONF_SEND_TIMEOUT, default='500ms'): cv.positive_time_period_milliseconds,
    cv.Optional(CONF_PUBLISH_ALL, default=True): cv.boolean,
    cv.Optional(CONF_TAGS, default={'node': CORE.name}): cv.Schema({
        cv.valid_name: cv.valid_name
    }),
    cv.Optional(CONF_SENSORS, default={}): SENSOR_SCHEMA,
}).extend(cv.COMPONENT_SCHEMA)


@coroutine_with_priority(40)
def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    yield cg.register_component(var, config)

    cg.add(var.set_server(config[CONF_SERVER]))
    cg.add(var.set_username(config[CONF_USERNAME]))
    cg.add(var.set_password(config[CONF_PASSWORD]))
    cg.add(var.set_database(config[CONF_DATABASE]))
    cg.add(var.set_measurement(config[CONF_MEASUREMENT]))
    cg.add(var.set_send_timeout(config[CONF_SEND_TIMEOUT]))
    cg.add(var.set_publish_all(config[CONF_PUBLISH_ALL]))

    cg.add(var.set_tags(''.join(',{}={}'.format(tag, value) for tag, value in config[CONF_TAGS].items())))

    for sensor_id, sensor_config in config[CONF_SENSORS].items():
        if not sensor_config[CONF_IGNORE]:
            tags = ''.join(',{}={}'.format(tag, value) for tag, value in {**config[CONF_TAGS] , **sensor_config[CONF_TAGS]}.items())
            if 'field' in sensor_config:
                field = f"\"{sensor_config[CONF_FIELD]}\""
            else:
                field = f"{sensor_id}->get_object_id()"
            cg.add(var.add_setup_callback(cg.RawExpression(f"[]() -> Nameable* {{ {sensor_id}->add_on_state_callback("
                                                           f"[](float state) {{ {config[CONF_ID]}->on_sensor_update("
                                                           f"{sensor_id}, {field}, \"{tags}\", state); }}); return"
                                                           f" {sensor_id}; }}")))
        else:
            cg.add(var.add_setup_callback(cg.RawExpression(f"[]() -> Nameable* {{ return {sensor_id}; }}")))

    cg.add_define('USE_INFLUXDB')
    cg.add_global(influxdb_ns.using)
