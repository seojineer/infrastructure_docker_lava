#!/bin/bash

# Copyright (c) 2016 Nexell Co., Ltd.
# Author: Sungwoo, Park <swpark@nexell.co.kr>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

set -e

CURRENT_PATH=`dirname $0`
TOOLS_PATH=`readlink -ev $CURRENT_PATH`
#SERIAL=$1
#DEVICE_PATH=$2

PARTMAP=
UPDATE_ALL=true
UPDATE_BL1=false
UPDATE_BL2=false
UPDATE_DISPATCHER=false
UPDATE_BOOTLOADER=false
UPDATE_ENV=false
UPDATE_BOOT=false
UPDATE_MODULES=false
UPDATE_ROOT=false
UPDATE_SYSTEM=false
UPDATE_DATA=false
UPDATE_DLOAD=false
RESULT_DIR=`readlink -ev $CURRENT_PATH/..`

MACHINE_NAME=
BOARD_SOCNAME=
BOARD_NAME=

function usage()
{
	echo "Usage: $0 [-t bl1] [-t bl2] [-t dispatcher] [-t uboot] [-t env] [-t kernel] [-t rootfs]"
	echo " -t bl1\t: if you want to update only bl1, specify this, default no"
        echo " -t bl2\t: if you want to update only bl2, specify this, default no ** s5p4418 only **"
        echo " -t armv7-dispatcher\t: if you want to update only armv7-dispatcher, specify this, default no ** s5p4418 only **"
	echo " -t uboot\t: if you want to update only bootloader, specify this, default no"
	echo " -t env\t: if you want to update only env, specify this, default no"
	echo " -t kernel\t: if you want to update only boot partition, specify this, default no"
	echo " -t rootfs\t: if you want to update only root partition, specify this, default no"
}

function vmsg()
{
	local verbose=${VERBOSE:-"false"}
	if [ ${verbose} == "true" ]; then
		echo "$@"
	fi
}

function parse_args()
{
    ARGS=$(getopt -o t:d:s:h -- "$@");
    eval set -- "$ARGS";

    while true; do
	case "$1" in
            -t ) case "$2" in
                    bl1    ) UPDATE_ALL=false; UPDATE_BL1=true ;;
                    bl2    ) UPDATE_ALL=false; UPDATE_BL2=true ;;
                    dispatcher  ) UPDATE_ALL=false; UPDATE_DISPATCHER=true ;;
                    uboot  ) UPDATE_ALL=false; UPDATE_BOOTLOADER=true ;;
                    env    ) UPDATE_ALL=false; UPDATE_ENV=true ;;
                    kernel ) UPDATE_ALL=false; UPDATE_BOOT=true ;;
                    rootfs ) UPDATE_ALL=false; UPDATE_ROOT=true ;;
		    *      ) usage; exit 1 ;;
                 esac
                 shift 2 ;;
            -s ) SERIAL=$2
                 shift 2 ;;
            -d ) DEVICE_PATH=$2
                 shift 2 ;;
            -h ) usage; exit 1 ;;
            -- ) break ;;
        esac
    done

    PARTMAP=$TOOLS_PATH/partmap_emmc.txt

    IFS='/' array=($RESULT_DIR)
    local temp="${array[-1]}"

    MACHINE_NAME=${temp#*-}
    BOARD_SOCNAME=${MACHINE_NAME%-*-*-*}
    T_BOARD_NAME=${MACHINE_NAME%-*}
    BOARD_NAME=${T_BOARD_NAME#*-}

    IFS=''
}

function print_args()
{
	vmsg "================================================="
	vmsg " print args"
	vmsg "================================================="
	vmsg -e "PARTMAP:\t\t${PARTMAP}"
	vmsg -e "RESULT_DIR:\t\t${RESULT_DIR}"
	if [ ${UPDATE_ALL} == "true" ]; then
		vmsg -e "Update:\t\t\tAll"
	else
		if [ ${UPDATE_BL1} == "true" ]; then
			vmsg -e "Update:\t\t\tbl1"
		fi
                if [ ${UPDATE_BL2} == "true" ]; then
			vmsg -e "Update:\t\t\tbl2"
		fi
                if [ ${UPDATE_DISPATCHER} == "true" ]; then
			vmsg -e "Update:\t\t\tarmv7_dispatcher"
		fi
		if [ ${UPDATE_BOOTLOADER} == "true" ]; then
		    if [ ${BOARD_SOCNAME} == "s5p6818" ]; then
			vmsg -e "Update:\t\t\tbootloader(fip files)"
		    else
			vmsg -e "Update:\t\t\tbootloader(singleimage)"
		    fi
		fi
		if [ ${UPDATE_ENV} == "true" ]; then
			vmsg -e "Update:\t\t\tenv"
		fi
		if [ ${UPDATE_BOOT} == "true" ]; then
			vmsg -e "Update:\t\t\tboot"
		fi
		if [ ${UPDATE_MODULES} == "true" ]; then
			vmsg -e "Update:\t\t\tmodules"
		fi
		if [ ${UPDATE_ROOT} == "true" ]; then
			vmsg -e "Update:\t\t\troot"
		fi
	fi
	vmsg
}

function flash()
{
	vmsg "flash $1 $2"
	sudo fastboot flash $1 $2 -s $SERIAL
}

function update_partmap()
{
	local partmap=${1}
	if [ ! -f ${partmap} ]; then
		echo "partmap file -- ${partmap} -- no exist!!!"
		exit 0
	fi

	flash partmap ${partmap}
}

function update_bl1()
{
	if [ ${UPDATE_ALL} == "true" ] || [ ${UPDATE_BL1} == "true" ]; then
		local file=${1}
		vmsg "update bl1: ${file}"
		flash 2ndboot ${file}
	fi
}

function update_bl2()
{
	if [ ${UPDATE_ALL} == "true" ] || [ ${UPDATE_BL2} == "true" ]; then
		local file=${1}
		vmsg "update bl2: ${file}"
		flash loader ${file}
	fi
}

function update_dispatcher()
{
	if [ ${UPDATE_ALL} == "true" ] || [ ${UPDATE_DISPATCHER} == "true" ]; then
		local file=${1}
		vmsg "update dispatcher: ${file}"
		flash blmon ${file}
	fi
}

function update_bootloader()
{
	if [ ${UPDATE_ALL} == "true" ] || [ ${UPDATE_BOOTLOADER} == "true" ]; then
		local file=${1}
		vmsg "update bootloader: ${file}"
		flash bootloader ${file}
	fi
}

function update_fip1()
{
	if [ ${UPDATE_ALL} == "true" ] || [ ${UPDATE_BOOTLOADER} == "true" ]; then
		local file=${1}
		vmsg "update loader: ${file}"
		flash fip-loader ${file}
	fi
}

function update_fip2()
{
	if [ ${UPDATE_ALL} == "true" ] || [ ${UPDATE_BOOTLOADER} == "true" ]; then
		local file=${1}
		vmsg "update secure: ${file}"
		flash fip-secure ${file}
	fi
}

function update_fip3()
{
	if [ ${UPDATE_ALL} == "true" ] || [ ${UPDATE_BOOTLOADER} == "true" ]; then
		local file=${1}
		vmsg "update nonsecure: ${file}"
		flash fip-nonsecure ${file}
	fi
}

function update_env()
{
	if [ ${UPDATE_ALL} == "true" ] || [ ${UPDATE_ENV} == "true" ]; then
		local file=${1}
		vmsg "update env: ${file}"
		flash env ${file}
	fi
}

function update_boot()
{
	if [ ${UPDATE_ALL} == "true" ] || [ ${UPDATE_BOOT} == "true" ]; then
		local file=${1}
		vmsg "update boot: ${file}"
		flash boot ${file}
	fi
}

function update_modules()
{
	if [ ${UPDATE_ALL} == "true" ] || [ ${UPDATE_MODULES} == "true" ]; then
		local file=${1}
		vmsg "update modules: ${file}"
		flash modules ${file}
	fi
}

function update_root()
{
	if [ ${UPDATE_ALL} == "true" ] || [ ${UPDATE_ROOT} == "true" ]; then
		local file=${1}
		vmsg "update rootfs: ${file}"
                flash rootfs ${file}
	fi
}

function update_system()
{
	if [ ${UPDATE_ALL} == "true" ] || [ ${UPDATE_SYSTEM} == "true" ]; then
		local file=${1}
		vmsg "update system: ${file}"
		flash system ${file}
	fi
}

function update_data()
{
	if [ ${UPDATE_ALL} == "true" ] || [ ${UPDATE_DATA} == "true" ]; then
		local file=${1}
		vmsg "update data: ${file}"
		flash user ${file}
	fi
}

function update_dload()
{
	if [ ${UPDATE_ALL} == "true" ] || [ ${UPDATE_DLOAD} == "true" ]; then
		local file=${1}
		vmsg "update dload: ${file}"
		flash dload ${file}
	fi
}

function fastboot_device_check()
{
	read_fastboot=`fastboot devices | grep $SERIAL`
	echo "$read_fastboot"

	case "$read_fastboot" in
		"")
			echo "nothing"
			echo -n $'\cc' > $DEVICE_PATH
			echo "fast 0" > $DEVICE_PATH
			sleep 4;;
			#exit;;
		*)
			echo "$SERIAL ok - ${1}";;
	esac
}

parse_args $@
print_args
echo "===============>"
echo -n $'\cc' > $DEVICE_PATH
echo "fast 0" > $DEVICE_PATH
sleep 4
update_partmap ${PARTMAP}

if [ "${BOARD_SOCNAME}" == "s5p6818" ]; then
	fastboot_device_check bl1
    update_bl1 ${RESULT_DIR}/bl1-emmcboot.img
	fastboot_device_check fip1
    update_fip1 ${RESULT_DIR}/fip-loader-emmc.img
	fastboot_device_check fip2
    update_fip2 ${RESULT_DIR}/fip-secure.img
	fastboot_device_check fip3
    update_fip3 ${RESULT_DIR}/fip-nonsecure.img
else
	fastboot_device_check bl1
    update_bl1 ${RESULT_DIR}/bl1-emmcboot.bin
	fastboot_device_check bl2
    update_bl2 ${RESULT_DIR}/loader-emmc.img
	fastboot_device_check dispatcher
    update_dispatcher ${RESULT_DIR}/bl_mon.img
	fastboot_device_check bootloader
    update_bootloader ${RESULT_DIR}/bootloader.img
fi

fastboot_device_check env
update_env ${RESULT_DIR}/params.bin
fastboot_device_check boot
update_boot ${RESULT_DIR}/boot.img
#fastboot_device_check root
echo -n $'\cc' > $DEVICE_PATH
echo "fast 0" > $DEVICE_PATH
sleep 4

update_root ${RESULT_DIR}/rootfs.img
echo "==============here!============"
if [ "${BOARD_NAME}" == "daudio-covi" -o "${BOARD_NAME}" == "daudio-cona" ]; then
	fastboot_device_check dload
	update_dload ${RESULT_DIR}/dload.img
	fastboot_device_check data
	update_data ${RESULT_DIR}/userdata.img
fi
#fastboot_device_check fastboot_continue
echo -n $'\cc' > $DEVICE_PATH
echo "fast 0" > $DEVICE_PATH
sleep 4
sudo fastboot continue -s $SERIAL
