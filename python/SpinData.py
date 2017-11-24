from GestureProcessor import SpinGestureProcessor, TestHarnessGestureProcessor
from Queue import Queue
from Phidget22.Devices.Encoder import *
import logging
from Phidget22.PhidgetException import *
import datetime

class SpinData:

    _all = set()
    _logger = None
    _spinner  = Encoder()
    _waitTimeForConnect = 5000
    
    def __init__(self,
                 config = {},
                 positionChange=0,
                 elapsedtime=0.0,
                 position=0):
        SpinData._all.add(self)
        self.config = config
        self.gestureProcessor = SpinGestureProcessor(self, config)
        self.position = position
        self.delta = positionChange
        self.timestamp = datetime.time()
        self.elapsedTime = elapsedtime
        self.spinHistory = Queue(config['encoderQueueLength'])
        
        if (SpinData._logger == None):
            SpinData._logger = logging.getLogger('spinsensorserver')

        try:
            SpinData._spinner.setOnAttachHandler(SpinData.encoderAttached)
            SpinData._spinner.setOnDetachHandler(SpinData.encoderDetached)
            SpinData._spinner.setOnErrorHandler(SpinData.encoderError)
                # _spinner.setOnInputChangeHandler(encoderInputChange)
            SpinData._spinner.setOnPositionChangeHandler(SpinData.encoderPositionChange)
        except PhidgetException as e:
            d = {'clientip': "spinner", 'user':"__init__"}
            SpinData._logger.critical('_spinner init failed: %s', 'details%s'% e.details, extra=d)
            SpinData._spinner = None
        try:
            SpinData._spinner.openWaitForAttachment(SpinData._waitTimeForConnect)
            SpinData._spinner.setDataInterval(SpinData._spinner.getMinDataInterval());
        except PhidgetException as e:
            d = {'clientip': "spinner", 'user':"open"}
            SpinData._logger.critical('_spinner connect failed: %s', 'details%s'% e.details, extra=d)
            SpinData._spinner = None


    def ingestSpinData(self, positionChange, time):
        self.delta = positionChange
        self.elapsedTime = time
        self.spinHistory.enqueue( positionChange * self.config['flipZ'])

    #Information Display Function
    def displayDeviceInfo():
        pass
        # print("|------------|----------------------------------|--------------|------------|")
        # print("|- Attached -|-              Type              -|- Serial No. -|-  Version -|")
        # print("|------------|----------------------------------|--------------|------------|")
        # if _spinner:
        #   print("|- %8s -|- %30s -|- %10d -|- %8d -|" % (_spinner.isAttached(), _spinner.getDeviceName(), _spinner.getSerialNum(), _spinner.getDeviceVersion()))
        #   print("|------------|----------------------------------|--------------|------------|")
        # if tilter:
        #   print("|- %8s -|- %30s -|- %10d -|- %8d -|" % (tilter.isAttached(), tilter.getDeviceName(), tilter.getSerialNum(), tilter.getDeviceVersion()))
        #   print("|------------|----------------------------------|--------------|------------|")
        #   print("Number of Acceleration Axes: %i" % (tilter.getAccelerationAxisCount()))
        #   print("Number of Gyro Axes: %i" % (tilter.getGyroAxisCount()))
        #   print("Number of Compass Axes: %i" % (tilter.getCompassAxisCount()))

    #Event Handler Callback Functions
    def encoderAttached(e):
        attached = e

        d = {'clientip': "spinner", 'user':"encoderAttached"}
        SpinData._logger.info('Encoder Attached! %s', 'good news', extra=d)

    def encoderDetached(e):
        detached = e
        d = {'clientip': "spinner", 'user':"encoderAttached" ()}
        SpinData._logger.warning('Encoder Detached: %s', detached.getDeviceSerialNumber(), extra=d)

    def encoderError(e, eCode, description):
        source = e
        d = {'clientip': "spinner", 'user':"encoderError"}
        SpinData._logger.error('Encoder error %s', description, extra=d)
 
    def encoderInputChange(e):
        source = e.device
        

    def encoderPositionChange(e, positionChange, timeChange, indexTriggered):
        source = e
        for spinner in SpinData._all:
            spinner.ingestSpinData(positionChange, timeChange)
