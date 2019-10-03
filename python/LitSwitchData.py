from GestureProcessor import SwitchGestureProcessor, TestHarnessGestureProcessor
from Queue import Queue

import logging
import datetime

class LitSwitchData:

    _all = set()
    _logger = None

    
    def __init__(self,
                 config = {},
                 switchConfig = {}):
        LitSwitchData._all.add(self)
        self.config = config
        self.config['outChar'] = switchConfig['outChar']
        self.sensor = switchConfig['hardware']
        self.gestureProcessor = SwitchGestureProcessor(self.sensor, config)
        
        self.timestamp = datetime.time()
        self.switchHistory = Queue(config['encoderQueueLength'])
        
        if (LitSwitchData._logger == None):
            LitSwitchData._logger = logging.getLogger('spinsensorserver')

        