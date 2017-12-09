import RPi.GPIO as IO
import time
  

class PWM():
    def __init__(self, channel):
        self.Channel = channel
        self.PulseController = ''
        self.DutyCycle=0

    def configure_PWM(self, frequency):
        IO.setmode(IO.BCM)
        IO.setup(self.Channel,IO.OUT)
        print(self.Channel, frequency)
        self.PulseController = IO.PWM(self.Channel, frequency)
        self.PulseController.start(0)

    def change_PW_elevation_gain(self, elevation_gain):
        if elevation_gain <0:
              self.DutyCycle=0
        else:
              self.DutyCycle = (20/3)*elevation_gain
        #print(duty_cycle)
        self.PulseController.ChangeDutyCycle(int(self.DutyCycle))
        
