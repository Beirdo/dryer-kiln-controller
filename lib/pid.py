# vim:ts=4:sw=4:ai:et:si:sts=4

import logging
import time
from threading import Lock, Thread


logger = logging.getLogger(__name__)


class PID(Thread):
    def __init__(self, kp, ki, kd, period, setpoint=None, delay=None, 
                 initial=None, off=None, input_callback=None,
                 output_callback=None):
        Thread.__init__(self)
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.period = period
        self.setpoint = setpoint or 0.0
        self.delay = delay or 0.0
        self.initial = initial or 0.0
        self.off = off
        self.input_callback = input_callback
        if not input_callback or not hasattr(input_callback, "__call__"):
            raise Exception("Unusable input_callback")
        self.output_callback = output_callback
        if not output_callback or not hasattr(output_callback, "__call__"):
            raise Exception("Unusable output_callback")
        self.last_input = 0.0
        self.limit_low = {}
        self.limit_high = {}
        self.integrator = self.initial
        self.daemon = True
        self.abort = False
        self.lock = Lock()

    def run(self):
        logger.info("Starting PID thread with period %.3fs, Kp: %f, Ki: %f, "
                    "Kd: %f, initial: %f, delay: %.3f, setpoint: %f" %
                    (self.period, self.kp, self.ki, self.kd, self.initial,
                     self.delay, self.setpoint))

        self.output_callback(self.initial)
        startTime = time.time()

        while not self.abort:
            loopStart = time.time()
            input_ = self.input_callback()

            with self.lock:
                kp = self.kp
                ki = self.ki
                kd = self.kd
                period = self.period
                setpoint = self.setpoint

            error = setpoint - input_
            delta = input_ - self.last_input
            self.last_input = input_

            if time.time() - startTime >= self.delay:
                self.integrator += ki * error
                self.integrator = self._limit(self.integrator, "integrator")

            output = kp * error + self.integrator - kd * delta
            output = self._limit(output, "output")
            self.output_callback(output)

            timeout = max(self.period - (time.time() - loopStart), 0.001)
            time.sleep(timeout)

        if self.off is not None:
            self.output_callback(self.off)

        logger.info("Ending PID thread")

    def _limit(self, value, key):
        with self.lock:
            limit_low = self.limit_low.get(key, None)
            if limit_low is not None:
                value = max(value, limit_low)
            limit_high = self.limit_high.get(key, None)
            if limit_high is not None:
                value = min(value, limit_high)
            return value

    def stop(self):
        self.abort = True

    def setCoefficients(self, kp, ki, kd):
        with self.lock:
            logger.info("Requested new coefficients: Kp: %f, Ki: %f, Kd: %f" %
                        (kp, ki, kd))
            self.kp = kp
            self.ki = ki
            self.kd = kd

    def setPeriod(self, period):
        with self.lock:
            logger.info("Requested a new period: %fs" % period)
            self.Period = period

    def setSetpoint(self, setpoint):
        with self.lock:
            logger.info("Requested a new setpoint: %fs" % setpoint)
            self.Period = setpoint

    def setLimit(self, key, limit_low, limit_high):
        with self.lock:
            logger.info("Requested new limits: %s <= %s <= %s" %
                        (limit_low, key, limit_high))

            if limit_low is None:
                self.limit_low.pop(key, None)
            else:
                self.limit_low[key] = limit_low

            if limit_high is None:
                self.high.pop(key, None)
            else:
                self.limit_high[key] = limit_high

