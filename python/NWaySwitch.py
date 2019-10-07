### switches.py
import RPi.GPIO as GPIO
from Switch import Switch
class NWaySwitch:
 
    _polesByPin = {}
    _currentPole = None
 
    _state = False
    def __init__(self,nodes):
        for node in nodes:
            switch = Switch(nodes[node]['switchpin'],
                            nodes[node]['ledpin'],
                            nodes[node]['LEDPullUpFlag'],
                            node, NWaySwitch.switch_detected)
            NWaySwitch._polesByPin[nodes[node]['switchpin']] = switch
            if 'default' in nodes[node]:
               NWaySwitch.switch_detected(nodes[node]['switchpin'])
        
    def newState(self):
        if NWaySwitch._state:
           NWaySwitch._state = False
           return True
        return False
    def get_keycode(self):
        return(NWaySwitch._currentPole.get_keycode())
    @classmethod
    def switch_detected(cls, pin):
        if (NWaySwitch._currentPole):
            if pin == NWaySwitch._currentPole.get_pin():
                return
            NWaySwitch._currentPole.LED.off()
        NWaySwitch._currentPole = NWaySwitch._polesByPin[pin]
        NWaySwitch._currentPole.LED.on()
        NWaySwitch._state = True
        
    
