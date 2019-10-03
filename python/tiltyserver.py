#!/usr/bin/python3

#Websockets imports
import asyncio
import datetime
import random
import websockets
import json
#Basic imports
from ctypes import *
import sys
import socket
import logging
import argparse
from LED import LED
from Switch import Switch
from  LitSwitchData import LitSwitchData
from shutil import copyfile

#Phidget specific imports

from Phidget22.PhidgetException import *
from Phidget22.Devices.Encoder import *
#from Phidget22.Devices.Spatial import *
#from Phidgets.Events.Events import AccelerationChangeEventArgs
from Phidget22.Devices.Accelerometer import *
from Phidget22.Phidget import *
from GestureProcessor import TiltGestureProcessor, SpinGestureProcessor, TestHarnessGestureProcessor
from Queue import Queue
from SpinData import SpinData
from TiltData import TiltData

parser = argparse.ArgumentParser(prog='tiltyserver', description='Serve Phidget sensor data via websocket.')
parser.add_argument('--localhost', action='store_true', 
                   help='force use of 127.0.0.1')
parser.add_argument('--port', '-p', 
                    type=int, dest='local_port_num',
                    default=5678,
                   help='set a tcp port for the server (default: 5678)')
parser.add_argument('--loglevel', nargs=1,
                    choices=['info', 'warning', 'debug', 'error', 'critical'],
                    default=['warning'],
                   help='set a log level for the server (default: warning; options: info, warning, debug, error, critical)') 
parser.add_argument('--logfilename', 
                    default='/var/log/tilty/server.log',
                   help='set a filename for logging (default: /var/log/tilty/server.log)')
parser.add_argument('--accelerometerQueueLength', 
                    type=int, dest='accelerometerQueueLength',
                    default=10,
                    help='queue length for averaging tilt data')
parser.add_argument('--encoderQueueLength', 
                    type=int, dest='encoderQueueLength',
                    default=1,
                    help='queue length for averaging spin data')
parser.add_argument('--tiltSampleRate', 
                    type=float, dest='tiltSampleRate',
                    default=0.01,
                    help='delay (in seconds?) to wait between sending message sets')
parser.add_argument('--tiltThreshold', 
                    type=float, dest='tiltThreshold',
                    default=0.002,
                    help='minimum accelerometer deflection from 0 to register as tilt')
parser.add_argument('--flipX', 
                    type=int, dest='flipX',
                    default=1,
                    help='change the logic of tilt along the left-right axis')
parser.add_argument('--flipY', 
                    type=int, dest='flipY',
                    default=-1,
                    help='change the logic of tilt along the near-far axis')
parser.add_argument('--flipZ', 
                    type=int, dest='flipZ',
                    default=-1,
                    help='change the logic of spin direction on zoom')

parser.add_argument('--swapXY', 
                    type=int, dest='swapXY',
                    default=0,
                    help='when the table gets rotated 90 wrt the projector')

parser.add_argument('--usePhidgets',
                    type=int, dest='usePhidgets',
                    default=1,
                    help='useful for testing switches or other non-phidget sensors')

parser.add_argument('--LEDpullUp',
            type=int, dest='LEDpullUp',
            default=1,
            help='logic for leds that go high or low')
args = parser.parse_args()

print(args)

numeric_level = getattr(logging, args.loglevel[0].upper(), None)
if not isinstance(numeric_level, int):
    raise ValueError('Invalid log level: %s' % args.loglevel[0].upper())
copyfile(args.logfilename, args.logfilename + '.previous')
#FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
FORMAT = '%(asctime)-15s  %(message)s'
logging.basicConfig(format=FORMAT, level=numeric_level, filename=args.logfilename, filemode='w', )
logger = logging.getLogger('sensorserver')
websocket_logger = logging.getLogger('websockets.server')
websocket_logger.setLevel(logging.ERROR)
websocket_logger.addHandler(logging.StreamHandler)

server_port = args.local_port_num

if (args.localhost):
    local_ip_address = "127.0.0.1"
else:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 1))  # connect() for UDP doesn't send packets
    local_ip_address = s.getsockname()[0]
d = {'clientip': local_ip_address, 'user': 'pi'}
logger.warning('Server starting: %s', 'defaults loaded %s %s' %(local_ip_address,args), extra=d)

config = {
    'accelerometerQueueLength': args.accelerometerQueueLength,
    'encoderQueueLength': args.encoderQueueLength,
    'tiltSampleRate' : args.tiltSampleRate,
    'tiltThreshold' : args.tiltThreshold,
    'flipX' : args.flipX,
    'flipY' : args.flipY,
    'flipZ' : args.flipZ,
    'swapXY' : args.swapXY,
    'LEDpullUp' : args.LEDpullUp,
}

if args.usePhidgets:
#Create an encoder object
    try:
        spindata = SpinData(config=config)
    except RuntimeError as e:

        d = {'clientip': local_ip_address, 'user': 'pi'}
        logger.error('Spin server starting error: %s', "Runtime spinner Exception: %s" % e.details, extra=d)
        # exit(1)
else:
    spindata = None
    
if args.usePhidgets:
    #Create an accelerometer object
    try:
        tiltdata = TiltData(config=config)

    except RuntimeError as e:
        print()
        print("Exiting....")
        d = {'clientip': local_ip_address, 'user': 'pi'}

        logger.error('Tilt server starting error: %s', "Runtime Exception: %s" % e.details, extra=d)
        exit(1)
else:
    tiltdata=None
    
litSwitches = {
         'e': { 'led' : LED(18,config), 'switch': Switch(4) }, 
         'c': { 'led' : LED(23,config), 'switch': Switch(17) }, 
         'j': { 'led' : LED(24,config), 'switch': Switch(27) }, 
         'k': { 'led' : LED(25,config), 'switch': Switch(22) }, 
         's': { 'led' : LED(12,config), 'switch': Switch(5) } 
    }
switchData = {}
for switch in ['e','c','j','k','s']:
    languageSensor = { 'outChar' : switch,
                                             'hardware': litSwitches[switch] }
    switchData[switch] = LitSwitchData(config, languageSensor)
        


testgp = None # TestHarnessGestureProcessor(None, config)

    
async def tilt(websocket, path):
    d = {'clientip': local_ip_address, 'user': 'pi', }
    logger.info('Websocket connection made: %s', "tilt server %s port %d path %s" % (websocket.remote_address[0], websocket.remote_address[1], path), extra=d)
    if tiltdata:
        tiltdata.level_table()
    try:
        logger.info('3 Websocket connection made: %s', "tilt server %s port %d path %s" % (websocket.remote_address[0], websocket.remote_address[1], path), extra=d)
        logger.info('preparing for polling %s', "hmmm %s" % "foo", extra=d)
        while True:
            now = datetime.datetime.utcnow().isoformat() + 'Z'
            #logger.info('polling %s', "hmmm %s" % "bar", extra=d)
                
            if (testgp and testgp.run()):
                outbound_message = testgp.nextAction()
                logger.info('sending test data: %s', "testgp next action=%s" % outbound_message, extra=d)
                try:
                    await websocket.send(outbound_message)
                except websockets.exceptions.ConnectionClosed:
                    d = {'clientip': local_ip_address, 'user': 'pi' }
                    logger.info('sending test data: %s', "client went away=%s" % outbound_message, extra=d)
                    break           
            for switch in switchData:
                #logger.info('polling switches: %s', "switch=%s" % repr(switchData[switch].gestureProcessor), extra=d)

                if (switchData[switch].gestureProcessor.run()):
                    outbound_message = switchData[switch].gestureProcessor.nextAction()
                    logger.info('sending switch data: %s', "switch nextAction=%s" % outbound_message, extra=d)
                    try:
                        await websocket.send(outbound_message)
                    except websockets.exceptions.ConnectionClosed:
                        logger.info('sending switch data: %s', "client went away=%s" % outbound_message, extra=d)
                        break
                #else:
                    #logger.info('no data switches: %s', "switch=%s" % repr(switchData[switch]), extra=d)
                    
            if (tiltdata and tiltdata.gestureProcessor.run()):
                try:
                    outbound_message = tiltdata.gestureProcessor.nextAction()
                    d = {'clientip': local_ip_address, 'user': 'pi'}
                    logger.info('sending tilt data: %s', "tilt nextAction=%s" % outbound_message, extra=d)
                except Exception:
                     logger.info('error sending tilt data: %s', "tilt nextAction=%s" % outbound_message, extra=d)
                try:
                    await websocket.send(outbound_message)
                except websockets.exceptions.ConnectionClosed:
                    d = {'clientip': local_ip_address, 'user': 'pi' }
                    logger.info('sending tilt data: %s', "client went away=%s" % outbound_message, extra=d)
                    break
            if (spindata and spindata.gestureProcessor.run()):
                outbound_message = spindata.gestureProcessor.nextAction()
                d = {'clientip': local_ip_address, 'user': 'pi' }
                logger.info('sending spin data: %s', "spin gp nextAction=%s" % outbound_message, extra=d)
                try:
                    await websocket.send(outbound_message)
                except websockets.exceptions.ConnectionClosed:
                    d = {'clientip': local_ip_address, 'user': 'pi' }
                    logger.info('sending spin data: %s', "client went away=%s" % outbound_message, extra=d)
                    break
            #await websocket.send(json.dumps(now))
            await asyncio.sleep(config['tiltSampleRate'])
    except  websockets.exceptions.ConnectionResetError:
        d = {'clientip': local_ip_address, 'user': 'pi', }
        logger.info('Websocket connection reset: %s', "tilt server %s port %d path %s" % (websocket.remote_address[0], websocket.remote_address[1], path), extra=d)
    d = {'clientip': local_ip_address, 'user': 'pi', }
    logger.info('Websocket connection ended: %s', "tilt server %s port %d path %s" % (websocket.remote_address[0], websocket.remote_address[1], path), extra=d)

#start_server = websockets.serve(tilt, '127.0.0.1', 5678)
#start_server = websockets.serve(tilt, '192.168.1.73', 5678)
#start_server = websockets.serve(tilt, '10.21.48.122', 5678)
start_server = websockets.serve(tilt, local_ip_address, server_port)
asyncio.get_event_loop().run_until_complete(start_server)
try:
    asyncio.get_event_loop().run_forever()
except:
    d = {'clientip': local_ip_address, 'user': 'pi', }
    logger.info('Uncaught error: %s', "%s" % (sys.exc_info()[0]))
   

