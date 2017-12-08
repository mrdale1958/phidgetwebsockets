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

parser = argparse.ArgumentParser(prog='tiltyserver', description='Serve Phidget sensor data via bluetooth.')
parser.add_argument('--localhost', action='store_true', 
                   help='force use of 127.0.0.1')
parser.add_argument('--port', '-p', 
                    type=int, dest='local_port_num',
                    default=5678,
                   help='set a tcp port for the server (default: 5678)')
parser.add_argument('--loglevel', nargs=1,
                    choices=['info', 'warning', 'debug', 'error', 'critical'],
                    default=['info'],
                   help='set a log level for the server (default: critical)') 
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
                    default=0.1,
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
parser.add_argument('--bt', 
                    dest='bt_mac_address',
                    default="B8:27:EB:38:4E:8E",
                    help='Bluetooth MAC address')
args = parser.parse_args()

print(args)

numeric_level = getattr(logging, args.loglevel[0].upper(), None)
if not isinstance(numeric_level, int):
    raise ValueError('Invalid log level: %s' % args.loglevel[0].upper())
copyfile(args.logfilename, args.logfilename + '.previous')
FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
logging.basicConfig(format=FORMAT, level=numeric_level, filename=args.logfilename, filemode='w', )
logger = logging.getLogger('sensorserver')
bt_logger = logging.getLogger('bts.server')
bt_logger.setLevel(logging.ERROR)
bt_logger.addHandler(logging.StreamHandler)

server_port = args.local_port_num
local_bt_address = args.bt_mac_address
#if (args.localhost):
#    local_bt_address = "127.0.0.1"
#else:
def serve(proc, addr, port):
    backlog = 1
    bt = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    bt.bind((addr, port))
    bt.listen(backlog)
    try:
        client, clientinfo = bt.accept()
        proc(client, "hmmm")
    except:
        client.close()
        bt.close()

d = {'clientip': local_bt_address, 'user': 'pi'}
logger.info('Server starting: %s', 'defaults loaded %s' %args, extra=d)

config = {
    'accelerometerQueueLength': args.accelerometerQueueLength,
    'encoderQueueLength': args.encoderQueueLength,
    'tiltSampleRate' : args.tiltSampleRate,
    'tiltThreshold' : args.tiltThreshold,
    'flipX' : args.flipX,
    'flipY' : args.flipY,
    'flipZ' : args.flipZ,
}

#Create an encoder object
try:
    spindata = SpinData(config=config)
except RuntimeError as e:

    d = {'clientip': local_bt_address, 'user': 'pi'}
    logger.error('Spin server starting error: %s', "Runtime spinner Exception: %s" % e.details, extra=d)
    # exit(1)

#Create an accelerometer object
try:
    tiltdata = TiltData(config=config)

except RuntimeError as e:
    print()
    print("Exiting....")
    d = {'clientip': local_bt_address, 'user': 'pi'}

    logger.error('Tilt server starting error: %s', "Runtime Exception: %s" % e.details, extra=d)
    exit(1)

  


testgp = None # TestHarnessGestureProcessor(None, config)

    
async def tilt(bt, path):
    d = {'clientip': local_bt_address, 'user': 'pi', }
    logger.info('bt connection made: %s', "tilt server %s port %d path %s" % (bt.remote_address[0], bt.remote_address[1], path), extra=d)
    tiltdata.level_table()
    try:
        while True:
            now = datetime.datetime.utcnow().isoformat() + 'Z'
            if (testgp and testgp.run()):
                outbound_message = testgp.nextAction()
                d = {'clientip': local_bt_address, 'user': 'pi' }
                logger.info('sending test data: %s', "testgp next action=%s" % outbound_message, extra=d)
                try:
                    await bt.send(outbound_message)
                except bts.exceptions.ConnectionClosed:
                    d = {'clientip': local_bt_address, 'user': 'pi' }
                    logger.info('sending test data: %s', "client went away=%s" % outbound_message, extra=d)
                    break           
            if (tiltdata.gestureProcessor.run()):
                outbound_message = tiltdata.gestureProcessor.nextAction()
                d = {'clientip': local_bt_address, 'user': 'pi'}
                logger.info('sending tilt data: %s', "tilt nextAction=%s" % outbound_message, extra=d)
                try:
                    await bt.send(outbound_message)
                except bts.exceptions.ConnectionClosed:
                    d = {'clientip': local_bt_address, 'user': 'pi' }
                    logger.info('sending tilt data: %s', "client went away=%s" % outbound_message, extra=d)
                    break
            if (spindata.gestureProcessor.run()):
                outbound_message = spindata.gestureProcessor.nextAction()
                d = {'clientip': local_bt_address, 'user': 'pi' }
                logger.info('sending spin data: %s', "spin gp nextAction=%s" % outbound_message, extra=d)
                try:
                    await bt.send(outbound_message)
                except websockets.exceptions.ConnectionClosed:
                    d = {'clientip': local_bt_address, 'user': 'pi' }
                    logger.info('sending spin data: %s', "client went away=%s" % outbound_message, extra=d)
                    break
            #await websocket.send(json.dumps(now))
            await asyncio.sleep(config['tiltSampleRate'])
    except  websockets.exceptions.ConnectionResetError:
        d = {'clientip': local_bt_address, 'user': 'pi', }
        logger.info('bt connection reset: %s', "tilt server %s port %d path %s" % (bt.remote_address[0], bt.remote_address[1], path), extra=d)
    d = {'clientip': local_bt_address, 'user': 'pi', }
    logger.info('bt connection ended: %s', "tilt server %s port %d path %s" % (bt.remote_address[0], bt.remote_address[1], path), extra=d)

#start_server = websockets.serve(tilt, '127.0.0.1', 5678)
#start_server = websockets.serve(tilt, '192.168.1.73', 5678)
#start_server = websockets.serve(tilt, '10.21.48.122', 5678)
start_server = serve(tilt, local_bt_address, server_port)
asyncio.get_event_loop().run_until_complete(start_server)
try:
    asyncio.get_event_loop().run_forever()
except:
    d = {'clientip': local_bt_address, 'user': 'pi', }
    logger.info('Uncaught error: %s', "%s" % (sys.exc_info()[0]))
   

