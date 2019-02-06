from GestureProcessor import TwistGestureProcessor, TestHarnessGestureProcessor
from Queue import Queue
from Phidget22.Devices.Encoder import *
import logging
from Phidget22.PhidgetException import *
import datetime

class TwistData:

    _all = set()
    _logger = None
    _twister  = [ Encoder(), Encoder() ]
    _waitTimeForConnect = 5000
    _channels = [0,1]
    
    def __init__(self,
                 config = {},
                 positionChange=0,
                 elapsedtime=0.0,
                 position=0):
        TwistData._all.add(self)
        self.config = config
        self.gestureProcessor = TwistGestureProcessor(self, config)
        self.position = position
        self.delta = positionChange
        self.deltas = [0,0,0,0]
        self.timestamp = datetime.time()
        self.elapsedTime = elapsedtime
        self.twistHistory = Queue(config['encoderQueueLength'])
        if 'channels' in config:
            _channels = config.channels
        else:
            _channels =  [0,2]
        
        if (TwistData._logger == None):
            TwistData._logger = logging.getLogger('twistsensorserver')

        try:
            for sensorNum in range(2):
                TwistData._twister[sensorNum].setOnAttachHandler(TwistData.encoderAttached)
                TwistData._twister[sensorNum].setOnDetachHandler(TwistData.encoderDetached)
                TwistData._twister[sensorNum].setOnErrorHandler(TwistData.encoderError)
                # _twister.setOnInputChangeHandler(encoderInputChange)
                TwistData._twister[sensorNum].setOnPositionChangeHandler(TwistData.encoderPositionChange)
            TwistData._twister[0] = _channels[0]
            TwistData._twister[1] = _channels[1]
        except PhidgetException as e:
            d = {'clientip': "twister", 'user':"__init__"}
            TwistData._logger.critical('_twister init failed: %s', 'details%s'% e.details, extra=d)
            TwistData._twister = None
        try:
            for sensorNum in range(2):
                TwistData._twister[sensorNum].openWaitForAttachment(TwistData._waitTimeForConnect)
                TwistData._twister[sensorNum].setDataInterval(TwistData._twister[sensorNum].getMinDataInterval());
        except PhidgetException as e:
            d = {'clientip': "twister", 'user':"open"}
            TwistData._logger.critical('_twister connect failed: %s', 'details%s'% e.details, extra=d)
            TwistData._twister = None


    def ingestTwistData(self, channel, positionChange, time):
        self.delta = 0
        for sensorNum in range(2):
            self.delta += TwistData._twister[sensorNum]
        ##self.deltas[channel] = positionChange
        ##sensordiff = 0
        ##for ch in range(4):
        ##    sensordiff = sensordiff - self.deltas[ch]
        self.elapsedTime = time
        self.twistHistory.enqueue( self.delta * self.config['flipZ'])

    #Information Display Function
    def displayDeviceInfo():
        pass

    #Event Handler Callback Functions
    def encoderAttached(e):
        attached = e
        try:
            print("\nAttach Event Detected (Information Below)")
            print("===========================================")
            print("Library Version: %s" % attached.getLibraryVersion())
            print("Serial Number: %d" % attached.getDeviceSerialNumber())
            print("Channel: %d" % attached.getChannel())
            print("Channel Class: %s" % attached.getChannelClass())
            print("Channel Name: %s" % attached.getChannelName())
            print("Device ID: %d" % attached.getDeviceID())
            print("Device Version: %d" % attached.getDeviceVersion())
            print("Device Name: %s" % attached.getDeviceName())
            print("Device Class: %d" % attached.getDeviceClass())
            print("\n")

        except PhidgetException as e:
            print("Phidget Exception %i: %s" % (e.code, e.details))
            print("Press Enter to Exit...\n")
            readin = sys.stdin.read(1)

        d = {'clientip': "twister", 'user':"encoderAttached"}
        TwistData._logger.info('Encoder Attached! %s', 'good news', extra=d)
        d = { 'clientip': "twister", 'user': "getMinPositionChangeTrigger %d getPositionChangeTrigger %d" %(attached.getMinPositionChangeTrigger(), attached.getPositionChangeTrigger())}
        TwistData._logger.critical('Encoder setup: %s', "hmmm", extra=d)

    def encoderDetached(e):
        detached = e
        d = {'clientip': "twister", 'user':"encoderDetached" }
        TwistData._logger.warning('Encoder Detached: %s', detached.getDeviceSerialNumber(), extra=d)

    def encoderError(e, eCode, description):
        source = e
#       d = {'clientip': "twister", 'user':"encoderError"}
#       TwistData._logger.error('Encoder error %s', description, extra=d)
 
    def encoderInputChange(e):
        source = e.getDeviceID()
        

    def encoderPositionChange(e, positionChange, timeChange, indexTriggered):
        source = e
        channel = e.getChannel()
        d = {'clientip': "twister", 'user':"encoderPositionChanged" }
        TwistData._logger.warning('Encoder update: %s', "%d %d" %(channel, positionChange), extra=d)
        this.ingestTwistData(channel, positionChange, timeChange)
