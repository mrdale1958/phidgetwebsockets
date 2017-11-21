#!/usr/bin/python3

import logging
import argparse
import socket


parser = argparse.ArgumentParser(prog='tiltyserver', description='Serve Phidget sensor data via websocket.')
parser.add_argument('--localhost', action='store_true', 
                   help='force use of 127.0.0.1')
parser.add_argument('--port', '-p', nargs=1,
                    type=int, dest='local_port_num',
                    default=5678,
                   help='set a tcp port for the server (default: 5678)')
parser.add_argument('--loglevel', nargs=1,
                    choices=['info', 'warning', 'debug', 'error', 'critical'],
                    default=['critical'],
                   help='set a log level for the server (default: critical)') 
parser.add_argument('--logfilename', nargs=1,
                    default='/var/log/tiltyserver.log',
                   help='set a filename for logging (default: /var/log/tiltyserver.log)') 
args = parser.parse_args()
print (vars(args))

print(args.localhost)
numeric_level = getattr(logging, args.loglevel[0].upper(), None)
if not isinstance(numeric_level, int):
    raise ValueError('Invalid log level: %s' % args.loglevel[0].upper())
FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
logging.basicConfig(format=FORMAT, level=numeric_level, filename=args.logfilename, filemode='w', )
logger = logging.getLogger('sensorserver')
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(('8.8.8.8', 1))  # connect() for UDP doesn't send packets
local_ip_address = s.getsockname()[0]
d = {'clientip': local_ip_address, 'user': 'pi'}
logger.info('Server started: %s', 'connection reset', extra=d)
