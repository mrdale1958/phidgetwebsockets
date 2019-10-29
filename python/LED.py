## LEDs.py
import RPi.GPIO as GPIO

class LED:
    
    
    def __init__(self,pin,LEDpullUpFlag=True):
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.pin,GPIO.OUT)
        self.status = False
        if LEDpullUpFlag:
            self.LEDOn = GPIO.HIGH
            self.LEDOff = GPIO.LOW
        else:
            self.LEDOn = GPIO.LOW
            self.LEDOff = GPIO.HIGH
        self.off()
        
    def on(self):
        GPIO.output(self.pin,self.LEDOn)
        self.status = True

    def off(self):
        #print("turning",self.pin,"off")
        GPIO.output(self.pin,self.LEDOff)
        self.status = False
       

    
    
