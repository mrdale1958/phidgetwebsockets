#!/usr/bin/env python

#Websockets imports
import asyncio
import datetime
import random
import websockets
import json
#Basic imports
from ctypes import *
import sys
#Phidget specific imports

from Phidgets.PhidgetException import PhidgetErrorCodes, PhidgetException
from Phidgets.Events.Events import AttachEventArgs, DetachEventArgs, ErrorEventArgs, EncoderPositionChangeEventArgs, InputChangeEventArgs
from Phidgets.Devices.Encoder import Encoder
from Phidgets.Events.Events import SpatialDataEventArgs
from Phidgets.Devices.Spatial import Spatial, SpatialEventData, TimeSpan
#from Phidgets.Events.Events import AccelerationChangeEventArgs
#from Phidgets.Devices.Accelerometer import Accelerometer
from Phidgets.Phidget import PhidgetLogLevel
from GestureProcessor import TiltGestureProcessor, SpinGestureProcessor, TestHarnessGestureProcessor

config = {
    'tiltHistoryLength':10,
    'spinHistoryLength':10,
    'accelerometerQueueLength':10,
    'encoderQueueLength':10,
    'tiltSampleRate' : 0.1,
    'tiltThreshold' : 0.002,
    'flipX' : 1,
    'flipY' : -1,
    'flipZ' : -1,
}
tilter = None
class Queue:
    def __init__(self, maxLength=10):
        self.items = []
        self.maxLength = maxLength

    def isEmpty(self):
        return self.items == []

    def enqueue(self, item):
        self.items.insert(0,item)
        if self.size() > self.maxLength:
            self.dequeue()
    
    def dequeue(self):
        if self.size():
            return self.items.pop()

    def head(self):
        if self.size():
            return self.items[0]
        return(0.0)

    def tail(self):
        if self.size():
            return self.items[self.size()-1]
        return(0.0)

    def size(self):
        return len(self.items)

class SpinData:
    def __init__(self, positionChange=0, elapsedtime=0.0, position=0):
        self.gestureProcessor = SpinGestureProcessor(self, config)
        self.position = position
        self.delta = positionChange
        self.timestamp = datetime.time()
        self.elapsedTime = elapsedtime
        self.spinHistory = Queue(config['encoderQueueLength'])

    def ingestSpinData(self, positionChange, time):
        self.delta = positionChange
        self.elapsedTime = time
        self.spinHistory.enqueue( positionChange * config['flipZ'])

class TiltData:

    def __init__(self):
        self.gestureProcessor = TiltGestureProcessor(self, config)
        self.components = [ Queue(config['accelerometerQueueLength']), Queue(config['accelerometerQueueLength']), Queue(config['accelerometerQueueLength']) ]
        self.variances =  [ Queue(config['accelerometerQueueLength']), Queue(config['accelerometerQueueLength']), Queue(config['accelerometerQueueLength']) ]
        self.magnitude = 0.0
        self.zeros = [ 0.0, 0.0, 0.0 ]

        self.serialNumber = ''

    def setZeros(self,x0,y0,z0):
        self.zeros = [ x0, y0, z0 ]

    def setAccelerometerZero(self, index, newZero):
        self.zeros[index] = newZero

    def ingestSpatialData(self, sensorData):
        if self.components[0].size() == 0:
            self.setZeros(sensorData.Acceleration[0],sensorData.Acceleration[1],sensorData.Acceleration[2])
        newX = config['flipX'] * (sensorData.Acceleration[0] - self.zeros[0])
        newY = config['flipY'] * (sensorData.Acceleration[1] - self.zeros[1])
        newZ = sensorData.Acceleration[2] - self.zeros[2]
        self.variances[0].enqueue(newX - self.components[0].head())
        self.variances[1].enqueue(newY - self.components[1].head())
        self.variances[2].enqueue(newZ - self.components[2].head())
        self.components[0].enqueue(newX)
        self.components[1].enqueue(newY)
        self.components[2].enqueue(newZ) 
     
    def ingestAccelerometerData(self, index, sensorData):
        if self.components[index].size() == 0:
            self.setAccelerometerZero(index,sensorData)
        newX = sensorData - self.zeros[index]
        self.variances[index].enqueue(newX - self.components[index].head())
        self.components[index].enqueue(newX)
 

                      
    def getJSON(self):
        jsonBundle = { 'type':        'tilt',
                    'packet': { 'sensorID':  '',
                    'tiltX': 0.0,
                    'tiltY': 0.0
                    }
                   }
                    
    
        return(JSON.dumps(jsonBundle))
    
#class SpinVector:



tiltVector = {
    'direction': [0.0,0.0],
    'magnitude': 0.0,
    'time': 0
    }

tiltHistory = Queue()

spinVector = { 
    'delta': 0.0,
    'rate':0.0,
    'time': 0
    }
spinHistory = Queue()


#Create an encoder object
try:
    spinner = Encoder()
    spindata = SpinData()
except RuntimeError as e:
    print("Runtime spinner Exception: %s" % e.details)
    print("Exiting....")
    # exit(1)

#Create an accelerometer object
try:
    spatial = Spatial()
#    accelerometer = Accelerometer()
    tiltdata = TiltData()

except RuntimeError as e:
    print("Runtime Exception: %s" % e.details)
    print("Exiting....")
    exit(1)

#Information Display Function
def displayDeviceInfo():
    pass
    # print("|------------|----------------------------------|--------------|------------|")
    # print("|- Attached -|-              Type              -|- Serial No. -|-  Version -|")
    # print("|------------|----------------------------------|--------------|------------|")
    # if spinner:
    #   print("|- %8s -|- %30s -|- %10d -|- %8d -|" % (spinner.isAttached(), spinner.getDeviceName(), spinner.getSerialNum(), spinner.getDeviceVersion()))
    #   print("|------------|----------------------------------|--------------|------------|")
    # if tilter:
    #   print("|- %8s -|- %30s -|- %10d -|- %8d -|" % (tilter.isAttached(), tilter.getDeviceName(), tilter.getSerialNum(), tilter.getDeviceVersion()))
    #   print("|------------|----------------------------------|--------------|------------|")
    #   print("Number of Acceleration Axes: %i" % (tilter.getAccelerationAxisCount()))
    #   print("Number of Gyro Axes: %i" % (tilter.getGyroAxisCount()))
    #   print("Number of Compass Axes: %i" % (tilter.getCompassAxisCount()))

#Event Handler Callback Functions
def encoderAttached(e):
    attached = e.device
    print("Encoder %i Attached!" % (attached.getSerialNum()))

def encoderDetached(e):
    detached = e.device
    print("Encoder %i Detached!" % (detached.getSerialNum()))

def encoderError(e):
    try:
        source = e.device
        print("Encoder %i: Phidget Error %i: %s" % (source.getSerialNum(), e.eCode, e.description))
    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))

def encoderInputChange(e):
    source = e.device
    print("Encoder %i: Input %i: %s" % (source.getSerialNum(), e.index, e.state))

def encoderPositionChange(e):
    source = e.device
    spindata.ingestSpinData(e.positionChange, e.time)
  
try:
    #logging example, uncomment to generate a log file
    #spinner.enableLogging(PhidgetLogLevel.PHIDGET_LOG_VERBOSE, "phidgetlog.log")

    spinner.setOnAttachHandler(encoderAttached)
    spinner.setOnDetachHandler(encoderDetached)
    spinner.setOnErrorhandler(encoderError)
    spinner.setOnInputChangeHandler(encoderInputChange)
    spinner.setOnPositionChangeHandler(encoderPositionChange)
except PhidgetException as e:
    print("Phidget spinner Error %i: %s" % (e.code, e.details))
    #exit(1)

print("Opening spinner phidget object....")

try:
    spinner.openPhidget()
except PhidgetException as e:
    print("Phidget spinner Error %i: %s" % (e.code, e.details))
    #exit(1)

print("Waiting for spinner attach....")

try:
    spinner.waitForAttach(10000)
except PhidgetException as e:
    print("Phidget spinner Error %i: %s" % (e.code, e.details))
    try:
        spinner.closePhidget()
        spinner = None
    except PhidgetException as e:
        print("Phidget Error %i: %s" % (e.code, e.details))
        #exit(1)
    #exit(1)
else:
    displayDeviceInfo()



#Event Handler Callback Functions
def SpatialAttached(e):
    attached = e.device
    print("Spatial %i Attached!" % (attached.getSerialNum()))

def SpatialDetached(e):
    detached = e.device
    print("Spatial %i Detached!" % (detached.getSerialNum()))

def SpatialError(e):
    try:
        source = e.device
        print("Spatial %i: Phidget Error %i: %s" % (source.getSerialNum(), e.eCode, e.description))
    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))

def SpatialData(e):
    source = e.device
    if tiltdata.serialNumber == source.getSerialNum():
        if tiltdata:
            tiltdata.ingestSpatialData(e.spatialData[0])
        # for index, spatialData in enumerate(e.spatialData):
        #     print("=== Data Set: %i ===" % (index))
        #     if len(spatialData.Acceleration) > 0:
        #         print("Acceleration> x: %6f  y: %6f  z: %6f" % (spatialData.Acceleration[0], spatialData.Acceleration[1], spatialData.Acceleration[2]))
        #     if len(spatialData.AngularRate) > 0:
        #         print("Angular Rate> x: %6f  y: %6f  z: %6f" % (spatialData.AngularRate[0], spatialData.AngularRate[1], spatialData.AngularRate[2]))
        #     if len(spatialData.MagneticField) > 0:
        #         print("Magnetic Field> x: %6f  y: %6f  z: %6f" % (spatialData.MagneticField[0], spatialData.MagneticField[1], spatialData.MagneticField[2]))
        #     print("Time Span> Seconds Elapsed: %i  microseconds since last packet: %i" % (spatialData.Timestamp.seconds, spatialData.Timestamp.microSeconds))
        
        # print("------------------------------------------")
    else:
        print("wrong device: expected-", tiltdata.serialNumber, "got-", source.getSerialNum())

#Main Program Code
try:
    #logging example, uncomment to generate a log file
    #spatial.enableLogging(PhidgetLogLevel.PHIDGET_LOG_VERBOSE, "phidgetlog.log")

    spatial.setOnAttachHandler(SpatialAttached)
    spatial.setOnDetachHandler(SpatialDetached)
    spatial.setOnErrorhandler(SpatialError)
    spatial.setOnSpatialDataHandler(SpatialData)
except PhidgetException as e:
    print("Phidget Exception %i: %s" % (e.code, e.details))
    print("Exiting....")
    spatial = None

print("Opening phidget object....")

try:
    spatial.openPhidget()
except PhidgetException as e:
    print("Phidget Exception %i: %s" % (e.code, e.details))
    print("Exiting....")
    spatial = None

print("Waiting for attach....")

try:
    spatial.waitForAttach(10000)
    tiltdata.serialNumber = spatial.getSerialNum()
    print('Attached spatial: ', tiltdata.serialNumber)
except PhidgetException as e:
    print("Phidget Exception %i: %s" % (e.code, e.details))
    try:
        spatial.closePhidget()
    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
        print("Exiting....")
        spatial = None
    print("Exiting....")
    spatial = None
else:
    spatial.setDataRate(4)
    #displayDeviceInfo()
# def AccelerometerAttached(e):
#     attached = e.device
#     print("Accelerometer %i Attached!" % (attached.getSerialNum()))

# def AccelerometerDetached(e):
#     detached = e.device
#     print("Accelerometer %i Detached!" % (detached.getSerialNum()))

# def AccelerometerError(e):
#     try:
#         source = e.device
#         print("Accelerometer %i: Phidget Error %i: %s" % (source.getSerialNum(), e.eCode, e.description))
#     except PhidgetException as e:
#         print("Phidget Exception %i: %s" % (e.code, e.details))

# def AccelerometerAccelerationChanged(e):
#     source = e.device
#     if tiltdata.serialNumber == source.getSerialNum():
#         if tiltdata:
#             tiltdata.ingestAccelerometerData(e.index, e.acceleration)
#     print("Accelerometer %i: Axis %i: %6f" % (source.getSerialNum(), e.index, e.acceleration))

# #Main Program Code
# try:
#     #logging example, uncomment to generate a log file
#     #accelerometer.enableLogging(PhidgetLogLevel.PHIDGET_LOG_VERBOSE, "phidgetlog.log")
    
#     accelerometer.setOnAttachHandler(AccelerometerAttached)
#     accelerometer.setOnDetachHandler(AccelerometerDetached)
#     accelerometer.setOnErrorhandler(AccelerometerError)
#     accelerometer.setOnAccelerationChangeHandler(AccelerometerAccelerationChanged)
# except PhidgetException as e:
#     print("Phidget accelerometer Exception %i: %s" % (e.code, e.details))
#     accelerometer = None

# print("Opening accelerometer object....")

# try:
#     accelerometer.openPhidget()
# except PhidgetException as e:
#     print("Phidget accelerometer Exception %i: %s" % (e.code, e.details))
#     accelerometer = None

# print("Waiting for accelerometer attach....")

# try:
#     accelerometer.waitForAttach(10000)
#     tiltdata.serialNumber = accelerometer.getSerialNum()
#     print('Attached accelerometer: ', tiltdata.serialNumber)
# except PhidgetException as e:
#     print("Phidget accelerometer Exception %i: %s" % (e.code, e.details))
#     try:
#         accelerometer.closePhidget()
#     except PhidgetException as e:
#         print("Phidget accelerometer Exception %i: %s" % (e.code, e.details))
#         accelerometer = None
#     accelerometer = None
# else:
#     try:
#         numAxis = accelerometer.getAxisCount()
#         accelerometer.setAccelChangeTrigger(0, 0.500)
#         accelerometer.setAccelChangeTrigger(1, 0.500)
#         if numAxis > 2:
#             accelerometer.setAccelChangeTrigger(2, 0.500)
#     except PhidgetException as e:
#         print("Phidget accelerometer Exception %i: %s" % (e.code, e.details))

if spatial:
    tilter = spatial
# else:
#     tilter = accelerometer 
#     accelerometer.setAccelChangeTrigger(0, 0.0100)
#     accelerometer.setAccelChangeTrigger(1, 0.0100)
#     print(accelerometer.getAccelChangeTrigger(0))

testgp = TestHarnessGestureProcessor(None, config)
async def tilt(websocket, path):
    print(path)
    while True:
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        if (testgp.run()):
            foo = testgp.nextAction()
            print(foo)
            await websocket.send(foo) 
        if (tiltdata.gestureProcessor.run()):
            await websocket.send(tiltdata.gestureProcessor.nextAction()) 
        if (spindata.gestureProcessor.run()):
            foo = spindata.gestureProcessor.nextAction()
            print(foo)
            await websocket.send(foo) 
        #await websocket.send(json.dumps(now))
        await asyncio.sleep(config['tiltSampleRate'])

start_server = websockets.serve(tilt, '127.0.0.1', 5678)
#start_server = websockets.serve(tilt, '192.168.1.89', 5678)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
