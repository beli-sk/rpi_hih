Raspberry Pi & HIHxxxx
======================

Reading of Honeywell HIHxxxx sensors on Raspberry Pi.


Requirements
------------

* `apt-get install python-smbus`
* `pip install py-zabbix` - optinal, for sending data to zabbix
* `apt-get install python-rpi.gpio` - optional, if reading multiple sensors powered by GPIO pins


Wiring
------

When reading only one sensor, connect Vcc to 3.3V output on RPi and set `SENSORS_GPIO = [None]`:

    HIHxxxx      RPi
    1 (Vcc) <--> P1-1 (3V3)
    2 (Vss) <--> P1-9 (GND)
    3 (SCL) <--> P1-5 (SCL1)
    4 (SDA) <--> P1-3 (SDA1)

To read multiple sensors, connect Vcc of each sensor to different GPIO pin, e.g. first one to P1-16 (GPIO23) and the second one to P1-18 (GPIO24) and then set `SENSORS_GPIO = [23, 24]`.
