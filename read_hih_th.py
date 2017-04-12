#!/usr/bin/env python
from __future__ import print_function, division
import time
import smbus
from pyzabbix import ZabbixMetric, ZabbixSender


bus = smbus.SMBus(1)
DEVICE_ADDRESS = 0x27
ZABBIX_SERVER = ''

bus.write_quick(DEVICE_ADDRESS)
data = bus.read_i2c_block_data(DEVICE_ADDRESS, 0, 4)

print(data)

status = (data[0] & 0xc0) >> 6;
rh = ((data[0] & 0x3f) * 256 + data[1]) / 0x3fff * 100;
temp = ((data[2] * 256 + data[3]) >> 2) / 0x3fff * 165 - 40;
print('status={} rh={:.4f} temp={:.4f}'.format(status, rh, temp))

packet = [
        ZabbixMetric('office_environment', 'hih.temp', temp),
        ZabbixMetric('office_environment', 'hih.rh', rh),
        ]

if not ZABBIX_SERVER:
    result = ZabbixSender(ZABBIX_SERVER).send(packet)
    print(result)
