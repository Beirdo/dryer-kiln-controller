# vim:ts=4:sw=4:ai:et:si:sts=4

import logging
import time
from threading import Lock, Thread


logger = logging.getLogger(__name__)


class SlowPWM(Thread):
    def __init__(self, period=1.0, io_callback=None):
        Thread.__init__(self)
        self.period = period
        self.newPeriod = period
        self.threshold = 0.0001 * self.period
        self.io_callback = io_callback
        if not io_callback or not hasattr(io_callback, "__call__"):
            raise Exception("Unusable io_callback")
        self.currDutyCycle = 0.0
        self.nextDutyCycle = 0.0
        self.ioHigh = False
        self.daemon = True
        self.abort = False
        self.lock = Lock()

    def run(self):
        logger.info("Starting SlowPWM thread with period %.3fs" % self.period)
        self.ioHigh = False
        with self.lock:
            self.currDutyCycle = self.nextDutyCycle
        self.io_callback(False)

        while not self.abort or not self.ioHigh:
            startTime = time.time()
            with self.lock:
                if self.ioHigh:
                    timeout = self.currDutyCycle * self.period
                else:
                    timeout = (1.0 - self.currDutyCycle) * self.period

            # adjust for lock wait time if any
            timeout -= (time.time() - startTime)

            # anything < 0.01% duty cycle is constant off
            # anything > 99.99% duty cycle is constant on
            if timeout >= self.threshold:
                self.io_callback(self.ioHigh)
                time.sleep(timeout)

            self.ioHigh = not self.ioHigh
            if self.ioHigh:
                if self.currDutyCycle != self.nextDutyCycle:
                    logger.info("New duty cycle taking effect: %f%%" %
                                (self.nextDutyCycle * 100.0))
                    self.currDutyCycle = self.nextDutyCycle

                if self.newPeriod != self.period:
                    logger.info("New period taking effect: %fs" %
                                self.newPeriod)
                    self.period = self.newPeriod
                    self.threshold = 0.0001 * self.period

        self.io_callback(False)
        logger.info("Ending SlowPWM thread with period %.3fs" % self.period)

    def stop(self):
        self.abort = True

    # input is % duty cycle.  Normalize to fraction of 1
    def setDutyCycle(self, dutyCycle):
        with self.lock:
            logger.info("Requested duty cycle: %f%%" % dutyCycle)
            dutyCycle /= 100.0
            logger.info("Normalized: %f" % dutyCycle)
            self.nextDutyCycle = min(max(dutyCycle, 0.0), 1.0)
            logger.info("Setting duty cycle to %f%%" % (self.nextDutyCycle * 100))

    def setPeriod(self, period):
        with self.lock:
            logger.info("Requested a new period: %fs" % period)
            self.newPeriod = period

