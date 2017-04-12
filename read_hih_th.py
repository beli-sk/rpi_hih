#!/usr/bin/env python
from __future__ import print_function, division
import sys
import time
import smbus


I2C_BUS = 1
DEVICE_ADDRESS = 0x27
ZABBIX_SERVER = ''
ZABBIX_HOST = ''
# To read multiple sensors, put here GPIO channels enabling them.
# Value of None omits GPIO control for a given sensor.
SENSORS_GPIO = [None]


if ZABBIX_SERVER:
    from pyzabbix import ZabbixMetric, ZabbixSender
    packet = []

active_gpios = [x for x in SENSORS_GPIO if x is not None]
if active_gpios:
    from RPi import GPIO
    GPIO.setmode(GPIO.BCM)
    for g in active_gpios:
        GPIO.setup(g, GPIO.OUT)
        GPIO.output(g, False)

try:
    bus = smbus.SMBus(I2C_BUS)
    for sen, sen_gpio in enumerate(SENSORS_GPIO):
        if sen_gpio is not None:
            GPIO.output(sen_gpio, True)
            time.sleep(0.1)
        try:
            bus.write_quick(DEVICE_ADDRESS)
        except IOError:
            sys.stderr.write('Sensor {:d} IO error.\n'.format(sen))
            continue
        data = bus.read_i2c_block_data(DEVICE_ADDRESS, 0, 4)
        if sen_gpio is not None:
            GPIO.output(sen_gpio, False)
        print(sen, data)
        status = (data[0] & 0xc0) >> 6
        rh = ((data[0] & 0x3f) * 256 + data[1]) / 0x3fff * 100
        temp = ((data[2] * 256 + data[3]) >> 2) / 0x3fff * 165 - 40
        print('sensor={:d} status={:d} rh={:.4f} temp={:.4f}'.format(sen, status, rh, temp))
        if ZABBIX_SERVER:
            packet = [
                    ZabbixMetric(ZABBIX_HOST, 'hih.temp[{:d}]'.format(sen), temp),
                    ZabbixMetric(ZABBIX_HOST, 'hih.rh[{:d}]'.format(sen), rh),
                    ]
    if ZABBIX_SERVER:
        result = ZabbixSender(ZABBIX_SERVER).send(packet)
        print(result)
finally:
    if active_gpios:
        GPIO.cleanup()

