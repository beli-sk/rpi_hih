Raspberry Pi & HumidIcon
========================

Reading of Honeywell HumidIcon HIH6xxx/HIH8xxx I2C sensors on Raspberry Pi.


Requirements
------------

* `apt-get install python-smbus`
* `apt-get install python-rpi.gpio`
* `pip install py-zabbix` - optinal, for sending data to zabbix


Wiring
------

When reading only one sensor, connect Vcc to 3.3V output on RPi:

    HIHxxxx      RPi
    1 (Vcc) <--> P1-1 (3V3)
    2 (Vss) <--> P1-9 (GND)
    3 (SCL) <--> P1-5 (SCL1)
    4 (SDA) <--> P1-3 (SDA1)

To read multiple sensors, connect Vcc of each sensor to different GPIO pin, e.g. first one to P1-16 (GPIO23) and the second one to P1-18 (GPIO24).


License
-------

Copyright 2017 Michal Belica <devel@beli.sk>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    
    You should have received a copy of the GNU General Public License
    along with the software.  If not, see <http://www.gnu.org/licenses/>.

A copy of the license can be found in the ``LICENSE`` file in the
distribution.

