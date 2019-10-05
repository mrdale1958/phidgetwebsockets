### switches.py
import RPi.GPIO as GPIO

class NWaySwitch:
 
    _polesByPin = {}
    _currentPole = None
 
    def __init__(self,nodes):
        for node in nodes:
            switch = Switch(nodes[node]['switchpin'],
                            nodes[node]['ledpin'],
                            nodes[node]['LEDPullUpFlag'],
                            node)
            if nodes[node]['default']:
                NWaySwitch.switch_detected(switch)
            NWaySwitch._polesByPin[nodes[node]['switchpin']] = switch
        

    @classmethod
    def switch_detected(cls, pin):
        if (NWaySwitch._currentPole):
            if pin == NWaySwitch._currentPole.get_pin():
                return
            NWaySwitch._currentPole.LED.off()
        NWaySwitch._currentPole = NWaySwitch._polesByPin[pin]
        NWaySwitch._currentPole.LED.on()
        print("switch",self.pin,"changed to",self.status)
        
    