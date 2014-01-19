import sys, serial, time, signal
from MFRC522 import MFRC522
from event import Event

class Sensor:

    # main program for reading and processing tags
    def __init__(self, name):
        self.name = name
        self.continue_reading = False
        self.tag_reader = MFRC522()
        self.signal = signal.signal(signal.SIGINT, self.end_read)

        self.last_tag = ''

        #EVENTS
        self.FOUND_TAG = Event()

    def end_read(self, signal,frame):
        print "Ctrl+C captured, ending read."
        self.stop()

    def stop(self):
        self.continue_reading = False

    def start(self):
        print "sensor running"
        self.continue_reading = True
        #if RFID is working - start monitoring it
        while self.continue_reading:
            (status,TagType) = self.tag_reader.MFRC522_Request(self.tag_reader.PICC_REQIDL)
         
            if status == self.tag_reader.MI_OK:
                print "Card detected"
         
            (status,backData) = self.tag_reader.MFRC522_Anticoll()
            if status == self.tag_reader.MI_OK:
                rfid_tag = "".join(str(val) for val in backData)
                print 'TAG : %s' % rfid_tag
                self.last_tag = rfid_tag
                self.FOUND_TAG(self) 

            time.sleep(.1)
        print 'not reading sensor'          
