import time
from collections import deque

from modules import cbpi
from modules.core.props import Property
from modules.core.hardware import ActorBase
from modules.core.controller import KettleController

try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)

except Exception as e:
    print
    e
    pass

@cbpi.actor
class HendiHeater(ActorBase):
    onoff_pin = Property.Select("On/Off GPIO", options = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27])
    power_pin = Property.Select("Power Control GPIO", options = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27])
    pwm_freq = Property.Number("PWM Frequency (Hz)", True, 100)
    power_limit = Property.Number("Maximum Power (%)", True, 100)

    power = 0
    pwm = None
    pwm_running = False

    def init(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(int(self.onoff_pin), GPIO.OUT)
        GPIO.setup(int(self.power_pin), GPIO.OUT)
        GPIO.output(int(self.onoff_pin), 0)
        self.pwm = GPIO.PWM(int(self.power_pin, int(self.pwm_freq)))

    def on(self, requested_power = 0):
        self.power = min(int(requested_power), int(self.power_limit))
        if self.pwm_running == False:
            self.pwm.start(int(self.power))
            self.pwm_running = True
        else:
            self.pwm.ChangeDutyCycle(int(self.power))
        if(self.power > 0):
            GPIO.output(int(self.onoff_pin), 1)

    def set_power(self, requested_power = 0):
        self.power = min(int(requested_power), int(self.power_limit))
        if self.pwm_running == False:
            self.pwm.start(int(self.power))
            self.pwm_running = True
        else:
            self.pwm.ChangeDutyCycle(int(self.power))

    def off(self):
        self.pwm.stop()
        self.pwm_running = False
        GPIO.output(int(self.onoff_pin), 0)

@cbpi.controller
class GradientPowerControl(KettleController):
    p_gradient_factor = Property.Number("Gradient Factor", True, 1)
    p_lookback_time = Property.Number("Lookback Time (s)", True, 15)
    p_mash_power_limit = Property.Number("Maximum Mash Power (%)", True, 50)
    p_boil_power = Property.Number("Boil Power (%)", True, 40)
    p_boil_threshold = Property.Number("Boil Power Threshold (°C)", True, 90)

    power = 0

    def run(self):
        gradient_factor = float(self.p_gradient_factor)
        lookback_time = int(self.p_lookback_time)
        mash_power_limit = float(self.p_mash_power_limit)
        boil_power = float(self.p_boil_power)
        boil_threshold = float(self.p_boil_threshold)

        temp_array = deque(maxlen=lookback_time) #lookback array
        for i in range(0, lookback_time): #initialize all elements with current temperature
            temp_array.append(self.get_temp())

        while self.is_running():
            target_temp = self.get_target_temp()
            current_temp = self.get_temp()
            
            gradient = temp_array[-1] - temp_array[0] #gradient = first and last element
            temp_array.append(current_temp) #update array

            diff = abs(target_temp - current_temp)
            self.power = mash_power_limit - (mash_power_limit / ((0.5 * diff) + 1)) #calculate power
            self.power = round(self.power, 1)

            if current_temp >= boil_threshold: #above boil threshold reduce power
                self.actor_power(boil_power)
                self.heater_on(power = boil_power)
            elif current_temp >= target_temp - (gradient * gradient_factor): #switch off heater depending on gradient
                self.heater_off()
            elif current_temp < target_temp: #heater on and update power
                self.actor_power(self.power)
                self.heater_on(power = self.power)
            
            self.sleep(1)

    def stop(self):
        super(KettleController, self).stop()
        self.heater_off()
