#!/bin/bash
#Create a qemu devices and add them to lava-server

# Add worker
lava-server manage workers add lava-slave
lava-server manage workers add lava-slave3

# Add device type
lava-server manage device-types add s5p4418-navi-qt-type

# Add device
lava-server manage devices add --device-type s5p4418-navi-qt-type --worker lava-slave s5p4418-navi-ref-qt

