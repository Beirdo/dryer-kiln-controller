# vim:ts=4:sw=4:ai:et:si:sts=4

import logging
from slowpwm import SlowPWM
from pid import PID


logger = logging.getLogger(__name__)


class Heater(object):
    def __init__(self, output_gpio, temperature_sensor, input_fan):
        self.output_gpio = output_gpio
        self.temperature_sensor = temperature_sensor
        self.input_fan = input_fan
        self.period = 5.0
        self.output_pwm = SlowPWM(period=self.period, io_callback=self.setGPIO)
        self.output_pwm.setDutyCycle(0.0)
        self.output_pwm.start()
        self.pid = None
        self.kp = 1.0  # needs tuning
        self.ki = 1.0  # needs tuning
        self.kd = 1.0  # needs tuning

    def power(self, onoff):
        if onoff and not self.pid:
            logger.info("Turning on heater")
            self.input_fan.force_power(True)
            self.pid = PID(self.kp, self.ki, self.kd, self.period,
                           input_callback=self.getTemperature,
                           output_callback=self.output_pwm.setDutyCycle)
            self.pid.setLimit("output", 0.0, 100.0)
            self.pid.setLimit("integrator", -100.0, 100.0)
            self.pid.start()
        elif not onoff and self.pid:
            logger.info("Turning off heater")
            self.pid.stop()
            self.pid.join()
            self.output_pwm.setDutyCycle(0.0)
            self.input_fan.force_power(False)
            self.pid = None

    def setTargetTemperature(self, target):
        if self.pid:
            logger.info("New target temperature: %.2fC" % target)
            self.pid.setSetpoint(target)

    def getTemperature(self):
        # read temperature sensor, return degrees Celsius
        temperature = 0.0
        logger.info("Temperature reading: %.2fC" % temperature)
        return temperature

    def setGPIO(self, onoff):
        # set the control GPIO on or off
        logger.info("Turning heater GPIO %s" % ("on" if onoff else "off"))
        return
