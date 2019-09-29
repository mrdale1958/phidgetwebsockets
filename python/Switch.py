### switches.py
import RPi.GPIO as GPIO

class Switch:
 
 
    def __init__(self,pin):
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.pin,GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.status = 0
#        print("switch",self.pin,"startss at",self.status)

        GPIO.add_event_detect(self.pin, GPIO.RISING, callback=self.switch_detected, bouncetime=200)

    def switch_detected(self, pin):
        self.status = 1
        print("switch",self.pin,"changed to",self.status)
        
    def clear(self):
        self.status = 0