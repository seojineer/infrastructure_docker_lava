#!/bin/bash

#stty -F /dev/ttyUSB0 115200 raw -echo -echoe -echok -echoctl -echoke
#Create a qemu devices and add them to lava-server

service ser2net restart
#sleep 3
#/etc/init.d/dbus start
