### switches.py
import RPi.GPIO as GPIO
from Switch import Switch
class NWaySwitch:
 
    _polesByPin = {}
    _polesByKeyCode = {}
    _currentPole = None
 
    _state = False
    def __init__(self,nodes):
        for node in nodes:
            switch = Switch(nodes[node]['switchpin'],
                            nodes[node]['ledpin'],
                            nodes[node]['LEDPullUpFlag'],
                            node, NWaySwitch.switch_detected)
            NWaySwitch._polesByPin[nodes[node]['switchpin']] = switch
            NWaySwitch._polesByKeyCode[node] = switch
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
    def consume_key(cls, key_code):
        if key_code == NWaySwitch._currentPole.get_keycode():
            NWaySwitch._currentPole.LED.off()
            return
        if key_code in NWaySwitch._polesByKeyCode:
            NWaySwitch._currentPole = NWaySwitch._polesByKeyCode[key_code]
            NWaySwitch._currentPole.LED.on()
            NWaySwitch._state = True

        
    @classmethod
    def switch_detected(cls, pin):
        if (NWaySwitch._currentPole):
            if pin == NWaySwitch._currentPole.get_pin():
                NWaySwitch._currentPole.LED.off()
                return
        NWaySwitch._currentPole = NWaySwitch._polesByPin[pin]
        NWaySwitch._currentPole.LED.on()
        NWaySwitch._state = True
        
    
