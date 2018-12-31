#!/bin/bash
#Create a qemu devices and add them to lava-server

# Add worker
#lava-server manage workers add lava-slave

# Add device type
lava-server manage device-types add s5p4418-navi-qt-type
lava-server manage device-types add qemu

# Add device
lava-server manage devices add --device-type s5p4418-navi-qt-type --worker new_lava_slave s5p4418-navi-ref-qt
lava-server manage devices add --device-type qemu --worker new_lava_slave qemu01

