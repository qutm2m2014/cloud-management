from manager.datastore import db, DateBaseModel, BaseModel
from sqlalchemy.dialects.postgresql import UUID as pgUUID, JSON as pgJSON
import uuid
import base64


def encode_uuid(id=None):
    if id is None:
        return uuid.uuid4().bytes.encode("base64")
    else:
        return id.bytes.encode("base64")


def decode_uuid(str):
    return uuid.UUID(base64.b64decode(str))


class APIKeys(BaseModel, DateBaseModel):
    # Extend to allow more granular authorization
    __tablename__ = 'api_keys'
    key = db.Column('key', db.String, primary_key=True, default=encode_uuid())
    default_key = db.Column('default_key', db.Boolean)
    device_id = db.Column('device_id', db.String, db.ForeignKey('devices.id'))


class DeviceTypes(BaseModel, DateBaseModel):
    __tablename__ = 'device_types'
    __show_in_json__ = ['device_types.name', 'device_types.devices', 'device_types.devices.serial_number']
    id = db.Column('id', pgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    activation_secret = db.Column('activation_secret', db.String, default=encode_uuid())
    name = db.Column('name', db.String)
    description = db.Column('description', db.Text)
    devices = db.relationship('Devices', order_by='Devices.id', backref='device_type')

    def __init__(self, name):
        self.name = name


class Devices(BaseModel, DateBaseModel):
    __tablename__ = 'devices'
    id = db.Column('id', db.Integer, primary_key=True)
    serial_number = db.Column('serial_number', db.String)
    activated = db.Column('activated', db.Boolean, default=False)
    device_type_id = db.Column('device_type', pgUUID(as_uuid=True), db.ForeignKey('device_types.id'))
    streams = db.relationship('Streams', order_by='Streams.id', backref='device')
    api_keys = db.relationship('APIKeys', order_by='APIKeys.key', backref='device')

    def __init__(self, serial_number, device_type_id):
        self.serial_number = serial_number
        self.device_type_id = device_type_id

class StreamDataType(BaseModel, DateBaseModel):
    __tablename__ = 'stream_data_types'
    data_type = db.Column('data_type', db.String, primary_key=True)


class Streams(BaseModel, DateBaseModel):
    __tablename__ = 'streams'
    id = db.Column('id', db.String, primary_key=True, default=encode_uuid())
    device_id = db.Column('device_id', db.Integer, db.ForeignKey('devices.id'))
    name = db.Column('name', db.String)
    value_schema = db.Column('value_schema', pgJSON)

    def __repr__(self):
        return 'Device ID: %s, Name: %s, Value Schema: %s' % (self.device_id, self.name, self.value_schema)


class Stream_Data(BaseModel, DateBaseModel):
    __tablename__ = 'stream_data'
    id = db.Column('id', db.String, primary_key=True, default=encode_uuid())
    value = db.Column('value', db.String)
