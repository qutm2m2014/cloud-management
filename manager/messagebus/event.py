

class Event():

    def __init__(self, device_type, serial_number, source_channel, payload):
        self.device_type = device_type
        self.serial_number = serial_number
        self.source_channel = source_channel
        self.payload = payload

    def __str__(self):
        return "Device Type: %s\nSerial Number: %s\nSource Channel: %s\nData: %s" % (self.device_type, self.serial_number, self.source_channel, self.payload)
