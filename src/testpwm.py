#! /usr/bin/env python3

import logging
import time
import sys
import os

baseDir = os.path.realpath(os.path.join(os.path.dirname(sys.argv[0]), ".."))
sys.path.append(os.path.join(baseDir, "lib"))

from slowpwm import SlowPWM

format = "%(asctime)s %(message)s"
logging.basicConfig(format=format, level=logging.DEBUG)
logger = logging.getLogger(__name__)

def callback(ioHigh):
    logger.info("ioHigh: %s" % ioHigh)

pwm = SlowPWM(period=10.0, io_callback=callback)
pwm.start()
pwm.setDutyCycle(50.0)
time.sleep(30.5)

pwm.setDutyCycle(10.0)
time.sleep(30.5)

pwm.setPeriod(5.0)
pwm.setDutyCycle(25.0)
time.sleep(30.5)

pwm.setDutyCycle(0.0)
time.sleep(30.5)

pwm.setDutyCycle(99.999)
time.sleep(20.5)

pwm.stop()
pwm.join()

