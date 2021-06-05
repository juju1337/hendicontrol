@cbpi.actor
class HendiHeater(ActorBase):
    onoff_pin = Property.Select("On/Off GPIO", options=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27])
    power_pin = Property.Select("Power Control GPIO", options=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27])
    pwm_freq = Property.Number("PWM Frequency (Hz)", configurable=True, default_value=100, unit="Hz")
    max_power = Property.Number("Limit Max Power (%)", configurable=True, default_value=100, unit="%")
    power = 0
    pwm = None

    def init(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(int(self.onoff_pin), GPIO.OUT)
        GPIO.setup(int(self.power_pin), GPIO.OUT)
        GPIO.output(int(self.onoff_pin), 0)
        self.Power = int(self.max_power)
        self.pwm = GPIO.PWM(int(self.power_pin, int(self.pwm_freq))

    def on(self, power):
        self.power = min(int(power), int(self.max_power))
        self.pwm.start(int(self.power))
        if(power > 0):
            GPIO.output(int(self.onoff_pin), 1)

    def set_power(self, power):
        self.power = min(int(power), int(self.max_power))
        self.pwm.ChangeDutyCycle(int(self.power))

    def off(self):
        self.pwm.stop()
        GPIO.output(int(self.onoff_pin), 0)
