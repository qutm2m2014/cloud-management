from flask import Blueprint, jsonify, Response, abort, request
from manager.datastore import models, db
from sqlalchemy.sql import func
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError
# from flask.ext.socketio import emit
from manager.extensions import socketio
import json
import hmac
from hashlib import sha1
import uuid

api = Blueprint('api', __name__, url_prefix="/api/v1")


def hex2uuid(hex):
    try:
        return uuid.UUID(hex=hex)
    except ValueError:
        abort(404)


@api.route("/devicetypes", methods=["GET"])
def list_device_types():
    """
    @api {get} /devicetypes List of Device Types
    @apiName GetDeviceTypes
    @apiGroup DeviceType

    @apiSuccess {Object} List Device Types
    """
    count_stmt = db.session.query(models.Devices.device_type_id, func.count('*').label("device_count")).group_by(models.Devices.device_type_id).subquery()
    results = db.session.query(models.DeviceTypes, count_stmt.c.device_count).outerjoin(count_stmt, models.DeviceTypes.id==count_stmt.c.device_type)

    device_types = []
    devices_metadata = {}
    for t, count in results:
        if count is None:
            count = 0
        devices_metadata[t.id] = {"count": count}
        device_types.append(t)

    return Response(json.dumps([dt.to_dict(show=['device_types.name', 'device_types.dt_created','device_types.id'], replace={"devices":devices_metadata[dt.id]}) for dt in device_types]),  mimetype='application/json')


@api.route("/devicetypes", methods=["POST"])
def new_device_type():
    if not request.json or not 'name' in request.json:
        abort(400)
    device = models.DeviceTypes(request.json["name"])
    db.session.add(device)
    db.session.commit()
    return jsonify(device=device.to_dict(show=['device_types.name'])), 201


@api.route("/devicetypes/<deviceType>", methods=["DELETE"])
def delete_device_type(deviceType):
    dt = models.DeviceTypes.query.filter_by(id=deviceType).first()
    if dt is None:
        abort(404)
    db.session.delete(dt)
    db.session.commit()
    return jsonify(result="Success"), 201


@api.route("/devicetypes/<deviceType>")
@api.route("/devicetypes/<deviceType>/devices", methods=["GET"])
def get_device_type(deviceType):
    deviceType = hex2uuid(deviceType)
    device_type = models.DeviceTypes.query.options(joinedload('devices')).filter_by(id=deviceType).first()
    if device_type is None:
        abort(404)
    return jsonify(
        device_type_metadata=device_type.to_dict(show=['device_types.name', 'device_types.dt_created','device_types.activation_secret']),
        devices=[dev.to_dict(show=['devices.serial_number','devices.activated'], hide=['devices.id']) for dev in device_type.devices]
        )


@api.route("/devicetypes/<deviceType>/devices", methods=["POST"])
def add_devices_to_device_type(deviceType):
    deviceType = hex2uuid(deviceType)
    ct = request.headers['Content-Type']
    if "text/plain" in ct:
        try:
            for sn in request.data.split("\n"):
                device = models.Devices(sn, deviceType)
                db.session.add(device)
            db.session.commit()
        except IntegrityError:
            jsonify(error="Serial Numbers must be unique"), 400
    else:
        jsonify(error="Only text/plain is accepted. CSV support is planned"), 400
    return jsonify(result="Success"), 201


@api.route("/devicetypes/<deviceType>/devices/<serialNumber>")
def show_device(deviceType, serialNumber):
    deviceType = hex2uuid(deviceType)
    device = models.Devices.query.options(joinedload('streams')).filter_by(serial_number=serialNumber).first()
    # typ, device = db.session.query(models.DeviceTypes, models.Devices).outerjoin(models.Devices, models.Devices.device_type_id==models.DeviceTypes.id).first()
    return jsonify(
        device=device.to_dict(path='device', show=['device.serial_number','device.dt_created', 'device.device_type.name', 'device.streams','device.streams.name','device.streams.value_schema'], hide=['device.streams.id','device.id'])
        )


@api.route("/devicetypes/<deviceType>/devices/<serialNumber>", methods=["DELETE"])
def delete_device(deviceType, serialNumber):
    device = models.Devices.query.filter_by(device_type_id=deviceType, serial_number=serialNumber).first()
    if device is None:
        abort(404)
    db.session.delete(device)
    db.session.commit()
    return jsonify(result="Success"), 201


@api.route("/devicetypes/<deviceType>/devices/<serialNumber>/activate", methods=["POST"])
def activate_device(deviceType, serialNumber):
    deviceType = hex2uuid(deviceType)
    #Check if device exists
    t, d = db.session.query(models.DeviceTypes, models.Devices).outerjoin(models.Devices, models.Devices.device_type_id==models.DeviceTypes.id).first()
    if t is None or d is None:
        return jsonify(error="Device not found"), 404

    print d.activated
    if d.activated:
        if 'X-M2M-API-KEY' in request.headers:
            api_key = db.session.query(models.APIKeys).outerjoin(models.Devices, models.Devices.id==models.APIKeys.device_id).filter(models.APIKeys.default_key==True, models.Devices.serial_number==serialNumber).first()
            print api_key
            if request.headers['X-M2M-API-KEY'] is api_key.key:
                return jsonify(api_key="abcdef")
        else:
            print "Returning error"
            return jsonify(error="Device already activated"), 400

    # As API key is invalid we must reauthenticate. Ensure request containes required credentials.
    if not request.form or not 'activation_code' in request.form:
        return jsonify(error="Malformed Request"), 403

    # What should the activation code be?
    our_hmac = hmac.new(str(t.activation_secret), str(d.serial_number), sha1).hexdigest()

    # Check if activation code is correct.
    if request.form["activation_code"] != our_hmac:
        return jsonify(error="Invalid activation code"), 403
    d.activated = True
    db.session.commit()
    return jsonify(api_key="abcdef")


@api.route("/devicetypes/<deviceType>/devices/<serialNumber>/streams/<streamName>")
def show_stream(deviceType, serialNumber, streamName):
    pass


@api.route("/devicetypes/<deviceType>/devices/<serialNumber>/streams", methods=["POST"])
def add_stream(deviceType, serialNumber):

    return ""


@socketio.on("connect", namespace="/devicetypes/<deviceType>/devices/<serialNumber>/streams/<streamName>")
def stream_connect(deviceType, serialNumber, streamName):
    pass
