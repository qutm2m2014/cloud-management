import paho.mqtt.client as paho
from event import Event
import multiprocessing as mp
import os

GRAPH = []


class ZeroMQEdge():
    pass


class Subprocess():

    """A class to manage subprocess"""

    process = None
    pid = 0
    exitstatus = 0
    target = None
    args = ()

    def __init__(self, target, args):
        self.target = target
        self.args = args
        self.process = mp.Process(target=self.target, args=self.args)

    def start(self):
        self.process.start()
        return


class Node():

    def get_pid():
        return os.getpid()


class ProcessingNode(Node):

    def __init__(self, inputs={}, outputs={}):
        pass


class OutputNode(Node):

    def __init__(self, outputs={}):
        pass


class InputNode(Node):
    def __init__(self, inputs={}):
        pass


class MQTTInput(InputNode):

    def __init__(self, topic, mqtt_broker_address="localhost", mqtt_broker_port=1884):
        self.topic = str(topic)
        self.mqtt_broker_port = mqtt_broker_port
        self.mqtt_broker_address = mqtt_broker_address

    def start(self):

        # Setup MQTT Subscriber
        mqttc = paho.Client()
        mqttc.connect(self.mqtt_broker_address, self.mqtt_broker_port, 60)
        mqttc.subscribe(self.topic, 0)

        def on_message(mosq, obj, msg):
            idArray = msg.topic.split("/")
            deviceType = idArray[0]
            serialNumber = idArray[1]
            channel = idArray[2]
            print "Recieved Data:"
            event = Event(deviceType, serialNumber, channel, msg.payload)
            print event

        mqttc.on_message = on_message

        rc = 0
        while rc is 0:
            mqttc.loop()
