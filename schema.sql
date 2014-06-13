
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;

CREATE EXTENSION "uuid-ossp";

BEGIN;

CREATE TABLE device_types (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(50) NOT NULL,
    description TEXT,
    activation_secret VARCHAR(60) NOT NULL,
    dt_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    dt_updated TIMESTAMP
);

INSERT INTO device_types (name, description, activation_secret) VALUES ('Atom','Devices created by the 2014 QUT M2M Team', '28034993c9c6d96e81a84483cbf21123');

CREATE TABLE devices (
    id SERIAL PRIMARY KEY,
    serial_number VARCHAR(100) NOT NULL,
    device_type UUID NOT NULL REFERENCES device_types (id) ON DELETE CASCADE ON UPDATE CASCADE,
    activated BOOLEAN DEFAULT FALSE,
    activated_on TIMESTAMP,
    dt_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    dt_updated TIMESTAMP,
    UNIQUE(device_type, serial_number)
);

INSERT INTO devices (serial_number,device_type) VALUES ('atom001', (SELECT id FROM device_types WHERE name='Atom'));

CREATE TABLE streams (
    id SERIAL PRIMARY KEY,
    device_id INTEGER NOT NULL REFERENCES devices (id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    name VARCHAR(50) NOT NULL,
    value_schema JSON NOT NULL,
    tags VARCHAR(50)[],
    dt_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    dt_updated TIMESTAMP,
    UNIQUE(device_id, name)
);

INSERT INTO streams (device_id, name, value_schema) VALUES ((SELECT id FROM devices WHERE serial_number='atom001'),'temperature1', '{"temperature":0}');

CREATE TABLE stream_data (
    stream_id INTEGER NOT NULL REFERENCES streams (id) ON DELETE CASCADE ON UPDATE CASCADE,
    value JSON NOT NULL,
    dt_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    dt_updated TIMESTAMP
);

CREATE TABLE api_keys (
    key VARCHAR(255) NOT NULL PRIMARY KEY,
    default_key BOOLEAN NOT NULL DEFAULT FALSE,
    device_id INTEGER NOT NULL REFERENCES devices (id) ON DELETE CASCADE ON UPDATE CASCADE,
    dt_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    dt_updated TIMESTAMP
);

CREATE UNIQUE INDEX ON api_keys (device_id) WHERE default_key;

COMMIT;
