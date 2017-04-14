#!/usr/bin/env python
from __future__ import print_function, division
import sys
import time
import smbus
from RPi import GPIO


class HumidIcon(object):
    """Honeywell HumidIcon 6xxx/8xxx sensor on I2C."""
    def __init__(self, bus, address, gpio, init=False):
        self.bus = bus
        self.address = address
        self.gpio = gpio
        self.initialized = False
        if init:
            self.gpio_setup()

    def gpio_setup(self):
        """Initialize GPIO channel. Don't forget to run GPIO.cleanup() when done."""
        if not self.initialized:
            self.initialized = True
            if self.gpio is not None:
                GPIO.setup(self.gpio, GPIO.OUT)
                GPIO.output(self.gpio, False)

    def read(self):
        """Read temperature and humidity.
        Return value: (status, rh, temp)
            status ... status returned by the sensor
            rh     ... relative humidity in %
            temp   ... templerature in degrees celsius
        Raises IOError.
        """
        self.gpio_setup()
        if self.gpio is not None:
            GPIO.output(self.gpio, True)
            time.sleep(0.1)
        bus.write_quick(self.address)
        time.sleep(0.04)
        data = bus.read_i2c_block_data(self.address, 0, 4)
        if self.gpio is not None:
            GPIO.output(self.gpio, False)
        status = (data[0] & 0xc0) >> 6
        rh = ((data[0] & 0x3f) * 256 + data[1]) / 0x3ffe * 100
        temp = ((data[2] * 256 + data[3]) >> 2) / 0x3ffe * 165 - 40
        return status, rh, temp

    def write_address(self, address):
        """Write new I2C slave address to sensor.
        The sensor must be powered by a GPIO pin.
        """
        self.gpio_setup()
        time.sleep(1)
        if self.gpio is None:
            raise Exception('Sensor must be powered by GPIO for configuration.')
        # power up
        GPIO.output(self.gpio, True)
        time.sleep(0.001)
        print('Entering command mode...')
        bus.write_i2c_block_data(self.address, 0xa0, [0, 0])
        time.sleep(0.001) # 1 ms
        # read command response
        data = bus.read_i2c_block_data(self.address, 0, 1)
        print('Response: 0x{:02x}'.format(data[0]))
        if data[0] != 0x81:
            print('Invalid response.')
            exit(1)
        print('Reading config...')
        bus.write_i2c_block_data(self.address, 0x1c, [0, 0])
        time.sleep(0.01)
        data = bus.read_i2c_block_data(self.address, 0, 3)
        print('Response: 0x{0[0]:02x} 0x{0[1]:02x}{0[2]:02x}'.format(data))
        if data[0] != 0x81:
            print('Invalid response.')
            exit(1)
        addr = data[2] & 0x7f
        print('Current address 0x{:02x}'.format(addr))
        print('Setting address 0x{:02x}'.format(address))
        wdata = [data[1], (data[2] & 0x80) | address]
        print('Writing config 0x{0[0]:02x}{0[1]:02x}...'.format(wdata))
        bus.write_i2c_block_data(self.address, 0x5c, wdata)
        time.sleep(0.05)
        # read command response
        data = bus.read_i2c_block_data(self.address, 0, 1)
        print('Response: 0x{:02x}'.format(data[0]))
        if data[0] != 0x81:
            print('Invalid response.')
            exit(1)
        print('Reading config...')
        bus.write_i2c_block_data(self.address, 0x1c, [0, 0])
        time.sleep(0.01)
        data = bus.read_i2c_block_data(self.address, 0, 3)
        print('Response: 0x{0[0]:02x} 0x{0[1]:02x}{0[2]:02x}'.format(data))
        if data[0] != 0x81:
            print('Invalid response.')
            exit(1)
        # power down
        GPIO.output(self.gpio, False)

def auto_int(x):
    return int(x, 0)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--bus', type=auto_int, default=1,
            help='I2C bus number (default: %(default)d)')
    parser.add_argument('-a', '--address', nargs='+', type=auto_int, default=[0x27],
            help='sensor addresses (default: 0x27)')
    parser.add_argument('-g', '--gpio', nargs='+', type=auto_int, help='GPIO pins powering sensors')
    parser.add_argument('-w', '--write', type=auto_int, help='write new address to sensor memory')
    parser.add_argument('-z', '--zabbix', action='store_true', help='send data to zabbix')
    parser.add_argument('-s', '--server', help='zabbix server address')
    parser.add_argument('-n', '--host', help='zabbix host name')
    args = parser.parse_args()
    if args.zabbix and not args.host:
        parser.error('Zabbix host is required if sending to zabbix is enabled.')
    if args.gpio and len(args.gpio) > 1 and len(args.address) > 1:
        parser.error('Only one of address or gpio can be a list.')
    if args.write is not None and (not args.gpio or len(args.gpio) > 1 or len(args.address) > 1):
        parser.error('Only one sensor powered by GPIO must be given when writing new address.')
    if args.write is not None and (args.write > 0x7f or args.write < 0
            or (args.write & 0x78) == 0 or (args.write & 0x78) == 0x78):
        parser.error('Invalid I2C address 0x{:02x}.'.format(args.write))

    # initialize Zabbix sender
    if args.zabbix:
        from pyzabbix import ZabbixMetric, ZabbixSender
        packet = []
        if args.server:
            sender = ZabbixSender(args.server)
        else:
            sender = ZabbixSender(use_config=True)
    else:
        sender = None

    # get I2C bus
    bus = smbus.SMBus(args.bus)

    # enumerating sensors
    sensors = []
    if args.gpio:
        GPIO.setmode(GPIO.BCM)
    if args.gpio and len(args.gpio) > 1:
        for gpio in args.gpio:
            sensors.append(HumidIcon(bus, args.address[0], gpio, init=True))
    else:
        for address in args.address:
            sensors.append(HumidIcon(bus, address, args.gpio[0] if args.gpio else None, init=True))

    # writing new address if requested
    if args.write is not None:
        if len(sensors) != 1:
            parser.error('Only one sensor can be given when writing is requested.')
        if sensors[0].gpio is None:
            parser.error('Sensor must be powered by GPIO pin if writing is requested.')
        sensors[0].write_address(args.write)
        GPIO.cleanup()
        sys.exit(0)

    # reading values
    for n, sensor in enumerate(sensors):
        try:
            status, rh, temp = sensor.read()
        except IOError:
            print('sensor={:d} status=error'.format(n))
            continue
        print('sensor={:d} status={:d} rh={:.4f} temp={:.4f}'.format(n, status, rh, temp))
        if sender:
            packet.extend([
                    ZabbixMetric(args.host, 'hih.temp[{:d}]'.format(n), temp),
                    ZabbixMetric(args.host, 'hih.rh[{:d}]'.format(n), rh),
                    ])
    if args.gpio:
        GPIO.cleanup()

    # sending values to Zabbix
    if sender:
        result = sender.send(packet)
        if getattr(result, 'failed', 0) > 0:
            sys.stderr.write(str(result) + '\n')
