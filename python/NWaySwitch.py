### switches.py
import RPi.GPIO as GPIO
from Switch import Switch
class NWaySwitch:
 
    
 
    _state = False
    def __init__(self,nodes):
        self.polesByPin = {}
        self.polesByKeyCode = {}
        self.currentPole = None
        self.stateChanged = False

        for node in nodes:
            self.key_code = node
            self.switch = Switch(nodes[node]['switchpin'],
                            nodes[node]['ledpin'],
                            nodes[node]['LEDPullUpFlag'],
                            node, self.switch_detected)
            self.polesByPin[nodes[node]['switchpin']] = self.switch
            self.polesByKeyCode[node] = self.switch
            if 'default' in nodes[node]:
               self.switch_detected(nodes[node]['switchpin'])

    
    def newState(self):
        if self.stateChanged:
           self.stateChanged = False
           return (True)
        return (False)

    def get_keycode(self):
        if (NWaySwitch._currentPole):
            return(NWaySwitch._currentPole.get_keycode())
        else:
            return(0)

    def consume_key(self, key_code):
        if self.currentPole && key_code != self.currentPole.get_keycode():
            self.currentPole.off()
            self.stateChanged = True
         else:
            return
        if key_code in self.polesByKeyCode:
            self.currentPole = self.polesByKeyCode[key_code]
            self.currentPole.on()

        
    def switch_detected(self, pin):
        if (self.currentPole):
            if pin != self.currentPole.get_pin():
                self.currentPole.off()
                self.stateChanged = True
            else:
                return
        self.currentPole = self.polesByPin[pin]
        self.currentPole.on()
        
    
