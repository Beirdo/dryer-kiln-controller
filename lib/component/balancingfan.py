# vim:ts=4:sw=4:ai:et:si:sts=4

import logging
from pid import PID


logger = logging.getLogger(__name__)


class BalancingFan(object):
    def __init__(self, output_fan, temperature_sensor):
        self.output_fan = output_fan
        self.temperature_sensor = temperature_sensor
        self.period = 0.5
        self.pid = None
        self.kp = 1.0  # needs tuning
        self.ki = 1.0  # needs tuning
        self.kd = 1.0  # needs tuning
        self.min_rpm = 500  # needs tuning
        self.max_rpm = 3600 # needs tuning

    def power(self, onoff):
        if onoff and not self.pid:
            logger.info("Turning on balancing fan")
            self.pid = PID(self.kp, self.ki, self.kd, self.period,
                           input_callback=self.getTemperature,
                           output_callback=self.setFanRPM,
                           output_filter_callback=abs)
            self.pid.setLimit("output", self.min_rpm, self.max_rpm)
            self.pid.setLimit("integrator", -self.max_rpm, self.max_rpm)
            self.pid.start()
        elif not onoff and self.pid:
            logger.info("Turning off balancing fan")
            self.pid.stop()
            self.pid.join()
            self.output_pwm.setFanRPM(0.0)
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

    def setFanRPM(self, speed):
        # set the fan speed
        logger.info("Setting fan speed to %s RPM" % speed)
        return
