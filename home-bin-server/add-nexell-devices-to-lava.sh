#!/bin/bash
#Create a qemu devices and add them to lava-server

# qemu
lava-server manage device-types add qemu
lava-server manage devices add --device-type qemu --worker new_lava_slave qemu01

# qemu02
lava-server manage device-types add qemu2
lava-server manage devices add --device-type qemu2 --worker new_lava_slave3 qemu02

# s5p4418-navi-ref-qt
lava-server manage device-types add s5p4418-navi-qt-type
lava-server manage devices add --device-type s5p4418-navi-qt-type --worker new_lava_slave s5p4418-navi-ref-qt

# imx8m example
lava-server manage device-types add imx8m-type
lava-server manage devices add --device-type imx8m-type --worker new_lava_slave imx8m-01

# s5p4418-navi-ref
lava-server manage device-types add s5p4418-navi-type
lava-server manage devices add --device-type s5p4418-navi-type --worker new_lava_slave s5p4418-navi-ref
