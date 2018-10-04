# vim:ts=4:sw=4:ai:et:si:sts=4

import logging
from threading import Thread, Lock


logger = logging.getLogger(__name__)


class InputFan(Thread):
    def __init__(self, output_fan, temperature_sensor, ambient_temp_sensor):
        Thread.__init__(self)
        self.daemon = True
        self.output_fan = output_fan
        self.temperature_sensor = temperature_sensor
        self.ambient_temperature_sensor = ambient_temp_sensor
        self.period = 2.0
        self.abort = False
        self.force = False
        self.onoff = False
        self.lock = Lock()
        self.setGPIO(False)

    def force_power(self, onoff):
        with self.lock:
            logger.info("%s input fan" % ("Forcing" if onoff else "Unforcing"))
            self.force = onoff

    def run(self):
        logger.info("Starting input fan control loop")
        while not self.abort:
            startTime = time.time()
            ambientTemperature = 0.0
            temperature = 0.0

            with self.lock:
                force = self.force
                old_onoff = self.onoff

            if not force:
                ambientTemperature = self.getAmbientTemperature()
                temperature = self.getTemperature()

            onoff = force or temperature > ambientTemperature
            if onoff != old_onoff:
                self.setGPIO(onoff)
                self.onoff = onoff

            delay = max(self.period - (time.time() - startTime), 0.001)
            time.sleep(delay)

        logger.info("Ending input fan control loop")

    def stop(self):
        self.abort = True

    def getTemperature(self):
        # read temperature sensor, return degrees Celsius
        temperature = 0.0
        logger.info("Temperature reading: %.2fC" % temperature)
        return temperature

    def getAmbientTemperature(self):
        # read ambient temperature sensor, return degrees Celsius
        temperature = 0.0
        logger.info("Ambient temperature reading: %.2fC" % temperature)
        return temperature

    def setGPIO(self, onoff):
        # set the control GPIO on or off
        logger.info("Turning input fan %s" % ("on" if onoff else "off"))
        Return
