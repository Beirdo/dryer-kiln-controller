# vim:ts=4:sw=4:ai:et:si:sts=4

import logging
from threading import Lock
import wiringpi


logger = logging.getLogger(__name__)


class TemperatureSensorBase(object):
    def __init__(self):
        pass

    def getTemperature(self):
        raise Exception("getTemperature not defined for %s" %
                        self.__class__.__name__)

    def getHumidity(self):
        raise Exception("getHumidity not defined for %s" %
                        self.__class__.__name__)



class SPISensor(Singleton):
    EXPANDER_BASE_PIN = 100
    def __init__(self):
        self.lock = Lock()
        # Setup pins for spi1, spi0
        wiringpi.pinMode(23, 1)
        wiringpi.pinMode(24, 1)
        wiringpi.wiringPiSPISetup(0, 4000000)
        wiringpi.pcf8574Setup(self.EXPANDER_BASE_PIN, 0x41)

    def getTemperature(self, device_num):
        device_num &= 0x3
        if wiringpi.digitalRead(self.EXPANDER_BASE_PIN + device_num):
            # Check the presence pin.  If no remote thermocouple connected,
            # this pin will be high.  If it's low, the remote thermocouple 
            # IS connected.
            return None

        spi1 = (device_num & 0x2) >> 1
        spi0 = device_num & 0x1
        with self.lock:
            # Set the SPI1/SPI0 pins
            wiringpi.digitalWrite(24, spi1)
            wiringpi.digitalWrite(24, spi0)
            buf = bytes([0, 0])
            retlen, retdata = wiringpi.wiringPiSPIDataRW(0, buf)

        # 16 bit return data.  bit 15 is a dummy sign bit (always 0)
        # bits 14-3 is 12-bit reading,
        # bit 2 is thermocouple input (high if open),
        # bit 1 is device id (always 0), bit 0 is state (tri-stated)
        if retlen != 2 or (retdata[1] & 0x04):
            logger.info("Bad reading or thermocouple open")
            return None
        
        # readings have a resolution of 0.25C
        reading = (retdata[0] << 5) + (retdata[1] >> 3)
        return float(reading / 4.0)


class MAX6675Thermocouple(TemperatureSensorBase):
    def __init__(self, device_num):
        self.device_num = device_num & 0x3
        TemperatureSensorBase.__init__(self)

    def getTemperature(self):
        return SPISensor().getTemperature(self.device_num)


class I2CBusMux(Singleton):
    def __init__(self):
        self.lock = Lock()
        self.i2cMux = wiringpi.wiringPiI2CSetup(0x70)

    def setBusMux(self, device_num):
        # Set the I2C bux mux
        device_num &= 0x3
        wiringpi.wiringPiI2CWrite(self.i2cMux, device_num)


# Si7021 or SHT20 Sensors
class Si7021Sensor(TemperatureSensorBase):
    def __init__(self, device_num):
        self.device_num = device_num & 0x3
        self.device_id = 0x40
        self.busMux = I2CBusMux()
        TemperatureSensorBase.__init__(self)

    def getTemperature(self):
        with self.busMux.lock:
            self.busMux.setBusMux(self.device_num)
            i2cDev = wiringpi.wiringPiI2CSetup(self.device_id)
            # Read both the humidity and the temperature, one measurement
            reading = wiringpi.wiringPiI2CReadReg16(i2cDev, 0xE3) >> 2

        return (175.72 * reading2) / 65536.0 - 46.85

    def getHumidity(self):
        with self.busMux.lock:
            self.busMux.setBusMux(self.device_num)
            i2cDev = wiringpi.wiringPiI2CSetup(self.device_id)
            # Read both the humidity and the temperature, one measurement
            reading1 = wiringpi.wiringPiI2CReadReg16(i2cDev, 0xE5) >> 2

        return (125.0 * reading1) / 65536.0 - 6.0
        

class EMC2301Controller(object):
    def __init__(self, device_num, poles=2):
        self.device_num = device_num & 0x3
        self.device_id = 0x2F
        self.poles = poles
        self.busMux = I2CBusMux()

    def getFanRPM(self)
        return 0

    def setFanRPM(self, speed):
        return




