## LEDs.py
import RPi.GPIO as GPIO

class LED:
    
    
    def __init__(self,pin):
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.pin,GPIO.OUT)
        self.status = False
        
    def on(self):
        GPIO.output(self.pin,GPIO.HIGH)
        self.status = True

    def off(self):
        #print("turning",self.pin,"off")
        GPIO.output(self.pin,GPIO.LOW)
        self.status = False
       

    
    