import RPi.GPIO as IO
import time
  

class PWM():
    def __init__(self, channel):
        self.Channel = channel
        self.PulseController = ''

    def configure_PWM(self, frequency):
        IO.setmode(IO.BCM)
        IO.setup(self.Channel,IO.OUT)
        print(self.Channel, frequency)
        self.PulseController = IO.PWM(self.Channel, frequency)
        self.PulseController.start(0)

    def change_PW_elevation_gain(self, elevation_gain):
        if elevation_gain <0:
              duty_cycle=100
        else:
              duty_cycle = 100-(20/3)*elevation_gain
        print(duty_cycle)
        self.PulseController.ChangeDutyCycle(int(duty_cycle))
        
