from GestureProcessor import SwitchGestureProcessor, TestHarnessGestureProcessor
from Queue import Queue
from NWaySwitch import NWaySwitch
import logging
import datetime

class LitNWaySwitchData:

    _logger = None

    
    def __init__(self,
                 config = {},
                 nodes = {}):
        self.config = config
        self.sensor = self.buildSwitch(nodes)
        self.gestureProcessor = SwitchGestureProcessor(self.sensor, config)
        
    def buildSwitch(self, nodes):
        return( NWaySwitch(nodes))

    def status(self):
        return(self.sensor.changed())

    def get_keycode(self):
        return(NWaySwitch._currentPole.get_keycode())


        