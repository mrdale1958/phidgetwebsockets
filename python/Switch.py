### switches.py
import RPi.GPIO as GPIO
from LED import LED
class Switch:
 
 
    def __init__(self,switchPin,LEDPin,LEDPullUpFlag,key_code,callback_fn):
        self.pin = switchPin
        self.key_code = key_code
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.pin,GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.LED = LED(LEDPin,LEDPullUpFlag)
        self.status = 0
#        print("switch",self.pin,"startss at",self.status)

        GPIO.add_event_detect(self.pin, 
                                GPIO.RISING, 
                                callback=callback_fn, 
                                bouncetime=200)

    def get_pin(self):
        return(self.pin)

    def get_keycode(self):
        return(self.key_code)

    def on(self):
        self.LED.on()

    def off(self):
        self.LED.off()
