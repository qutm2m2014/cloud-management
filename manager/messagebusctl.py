from messagebus import MQTTVent
from datastore import db
from datastore.models import Streams, Devices
import multiprocessing as mp


processes = []


class MBProcess:

    def __init__(self, topic, process):
        self.process = process
        self.topic = topic


def run():
    print "\nStarting Message Bus"
    q = db.session.query(Devices).outerjoin(Streams, Streams.device_id == Devices.id).all()
    for device in q:
        for stream in device.streams:
            print "Device Type: %s" % device.device_type.id
            print "Device: %s" % device.serial_number
            print "Stream: %s" % stream
            topic = "%s/%s/%s" % (device.device_type.id, device.serial_number, stream.name)
            vent = MQTTVent(topic)
            p = mp.Process(target=vent.start)
            mbp = MBProcess(topic, p)
            processes.append(mbp)

    for mbp in processes:
        print "Starting process for: %s" % mbp.topic
        mbp.process.start()

    print "\n"
