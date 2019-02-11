#!/bin/bash
#Create a qemu devices and add them to lava-server

# qemu
lava-server manage device-types add qemu
lava-server manage devices add --device-type qemu --worker new_lava_slave3 qemu01
lava-server manage devices add --device-type qemu --worker new_lava_slave3 qemu02

# s5p4418-navi
lava-server manage device-types add s5p4418-navi-ref-type
lava-server manage devices add --device-type s5p4418-navi-ref-type --worker new_lava_slave s5p4418-navi-ref-qt
lava-server manage devices add --device-type s5p4418-navi-ref-type --worker new_lava_slave s5p4418-navi-ref-tiny
lava-server manage devices add --device-type s5p4418-navi-ref-type --worker new_lava_slave s5p4418-navi-ref

# convergence
lava-server manage device-types add s5p4418-convergence-svmc-type
lava-server manage devices add --device-type s5p4418-convergence-svmc-type --worker new_lava_slave3 s5p4418-convergence-svmc

# s5p6818-avn
lava-server manage device-types add s5p6818-avn-ref-type
lava-server manage devices add --device-type s5p6818-avn-ref-type --worker new_lava_slave3 s5p6818-avn-ref
