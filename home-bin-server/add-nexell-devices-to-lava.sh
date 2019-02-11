#!/bin/bash
#Create a qemu devices and add them to lava-server

# qemu
lava-server manage device-types add qemu
lava-server manage devices add --device-type qemu --worker new_lava_slave qemu01
lava-server manage devices add --device-type qemu --worker new_lava_slave qemu02

lava-server manage device-types add s5p4418-navi-ref-type
lava-server manage devices add --device-type s5p4418-navi-ref-type --worker new_lava_slave s5p4418-navi-ref-qt
lava-server manage devices add --device-type s5p4418-navi-ref-type --worker new_lava_slave s5p4418-navi-ref-tiny
lava-server manage devices add --device-type s5p4418-navi-ref-type --worker new_lava_slave s5p4418-navi-ref
