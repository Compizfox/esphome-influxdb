#pragma once

#include <vector>
#include "esphome/core/component.h"
#include "esphome/core/controller.h"
#include "esphome/core/defines.h"
#include "esphome/core/log.h"

#include "esphome/components/http_request/http_request_arduino.h"

namespace esphome {
	namespace influxdb {
		class InfluxDBWriter : public Component {
		public:
			InfluxDBWriter() {};
			void setup() override;
			void dump_config() override;
#ifdef USE_BINARY_SENSOR
			void on_sensor_update(binary_sensor::BinarySensor *obj, std::string field, std::string tags, bool state);
#endif
#ifdef USE_SENSOR
			void on_sensor_update(sensor::Sensor *obj, std::string field, std::string tags, float state);
#endif
#ifdef USE_TEXT_SENSOR
			void on_sensor_update(text_sensor::TextSensor *obj, std::string field, std::string tags, std::string state);
#endif
			void set_server(std::string server) { this->server = server; };
			void set_username(std::string username) { this->username = username; };
			void set_password(std::string password) { this->password = password; };
			void set_database(std::string database) { this->database = database; };
			void set_measurement(std::string measurement) { this->measurement = measurement; };
			void set_send_timeout(int timeout) { send_timeout = timeout; };
			void set_tags(std::string tags) { this->tags = tags; };
			void set_publish_all(bool all) { publish_all = all; };
			void add_setup_callback(std::function<EntityBase * ()> fun) { setup_callbacks.push_back(fun); };

		protected:
			void write(std::string field, std::string tags, std::string value, bool is_string);

			std::string server;
			std::string username;
			std::string password;
			std::string database;
			std::string measurement;
			std::string service_url;
			std::list<http_request::Header> headers;

			int send_timeout;
			std::string tags;
			bool publish_all;

			std::vector<std::function<EntityBase * ()>> setup_callbacks;

			http_request::HttpRequestArduino *request_;
		};

	} // namespace influxdb
} // namespace esphome
