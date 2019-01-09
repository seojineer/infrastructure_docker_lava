#!/bin/bash

set -e

CURRENT_PATH=`dirname $0`
argc=$#

COMMAND_TYPE=$1
DOWNLOAD_DIR_NAME=$2
#USB_BUS_NUM=$3
DEVICE_PATH=$3

function run_command()
{
    local command=${COMMAND_TYPE}
    local path=${DOWNLOAD_DIR_NAME}
    #local usb_num=${USB_BUS_NUM}
	echo $command

    if [ "$command" == "reboot-bootloader" ]; then
		echo " " > "${DEVICE_PATH}"; sleep 1
		echo " " > "${DEVICE_PATH}"; sleep 1
        echo "root" > "${DEVICE_PATH}"; sleep 3
        echo "root" > "${DEVICE_PATH}"; sleep 3
        echo "reboot" > "${DEVICE_PATH}"; sleep 10

		# android
		if [ "$path" == "result-s5p4418-navi_ref" ] || [ "$path" == "result-clova" ] || [ "$path" == "result-s5p4418-navi_ref_quickboot" ] || [ "$path" == "result-s5p4418-avn_ref" ] || [ "$path" == "result-s5p4418-avn_ref_quickboot" ] || [ "$path" == "result-s5p6818-avn_ref" ] || [ "$path" == "result-s5p6818-avn_ref_quickboot" ]; then
			echo "android"
			cp /opt/share/update.sh /opt/share/$path/
			cd /opt/share/$path

			/opt/share/$path/boot_by_usb.sh

		# yocto
		else
			echo "yocto"
			#cp /opt/share/standalone-fastboot-download.sh /opt/share/$path/tools/standalone-fastboot-download.sh
			/opt/share/$path/tools/standalone-uboot-by-usb-download.sh

			echo "yocto uboot" >> /opt/share/log.txt
		fi

        for ((i=0;i<1000;i++)); do
            echo " " > "${DEVICE_PATH}"
        done

        sleep 2
       
	# change fastboot serial number 
	echo "setenv serial# ${path:7}" > "${DEVICE_PATH}"; sleep 5
	echo " " > "${DEVICE_PATH}"
	echo "setenv serial# ${path:7}" > "${DEVICE_PATH}"; sleep 5
        echo "fast 0" > "${DEVICE_PATH}"; sleep 1
        
	echo "OKAY"
	echo "======================================="
        echo "Success, usb-download!"; sleep 1
        echo "======================================="

    elif [ "$command" == 'fastboot-download' ]; then
		# android
		echo $path
		if [ "$path" == "result-s5p4418-navi_ref" ] || [ "$path" == "result-clova" ] || [ "$path" == "result-s5p4418-navi_ref_quickboot" ] || [ "$path" == "result-s5p4418-avn_ref" ] || [ "$path" == "result-s5p4418-avn_ref_quickboot" ] || [ "$path" == "result-s5p6818-avn_ref" ] || [ "$path" == "result-s5p6818-avn_ref_quickboot" ]; then
			echo "android"
			cd /opt/share/$path/
			/opt/share/$path/update.sh ${path:7} ${DEVICE_PATH}

		# yocto
		else
			echo "yocto"
			sudo /opt/share/$path/tools/standalone-fastboot-download.sh ${path:7} ${DEVICE_PATH}
			echo "/opt/share/$path/tools/standalone-fastboot-download.sh ${path:7} $DEVICE_PATH" >> /opt/share/log.txt
		fi

        sleep 3
        
        echo "OKAY"
		echo "======================================="
        echo "Success, fastboot-download!"
        echo "======================================="

    elif [ "$command" == 'running' ]; then
        #echo " " > "${DEVICE_PATH}"
        echo "OKAY"
        echo "======================================="
        echo "Success, Nexell Ready for Test!"
        echo "======================================="
        
    elif [ "$command" == 'boot-on-uboot' ]; then
		echo " " > "${DEVICE_PATH}"; sleep 15
        echo "boot" > "${DEVICE_PATH}"; sleep 10
		echo "root" > "${DEVICE_PATH}"; sleep 3
        echo "root" > "${DEVICE_PATH}"; sleep 3
        echo "root" > "${DEVICE_PATH}"; sleep 3
		sleep 15
		echo "/usr/bin/start_adbd.sh" > "${DEVICE_PATH}"; sleep 3
        echo "/usr/bin/start_adbd.sh" > "${DEVICE_PATH}"; sleep 3
        echo "/usr/bin/start_adbd.sh" > "${DEVICE_PATH}"; sleep 3
        echo "/usr/bin/start_adbd.sh" > "${DEVICE_PATH}"; sleep 3
        echo "/usr/bin/start_adbd.sh" > "${DEVICE_PATH}"; sleep 3
		echo " " > "${DEVICE_PATH}"
		echo "OKAY"
        echo "======================================="
        echo "Success, reset after fastboot download!"
        echo "======================================="

    elif [ "$command" == 'run-uboot-by-usb' ]; then
        run_uboot_by_usb_download $path

    elif [ "$command" == 'test1' ]; then
		echo "test1"
		echo "test1" >> /opt/share/log.txt
		echo " " > "${DEVICE_PATH}"
		echo "${DEVICE_PATH}" >> /opt/share/log.txt

    elif [ "$command" == 'test2' ]; then
		echo "test2"
		echo "test2" >> /opt/share/log.txt

    elif [ "$command" == 'enter' ]; then
    	echo "enter"
		echo "enter" >> /opt/share/log.txt
		echo " " > "${DEVICE_PATH}"; sleep 1
		echo " " > "${DEVICE_PATH}"; sleep 1
		echo " " > "${DEVICE_PATH}"; sleep 1
		echo " " > "${DEVICE_PATH}"; sleep 1
		echo " " > "${DEVICE_PATH}"; sleep 1

    # yocto - change serial name and boot
    elif [ "$command" == 'uboot-serial' ]; then
		echo "uboot-serial" >> /opt/share/log.txt

		echo " " > "${DEVICE_PATH}"; sleep 5
        echo "boot" > "${DEVICE_PATH}"; sleep 15
		echo " " > "${DEVICE_PATH}"; sleep 2
		echo " " > "${DEVICE_PATH}"; sleep 1
		echo "root" > "${DEVICE_PATH}"; sleep 3
		echo "root" > "${DEVICE_PATH}"; sleep 3
        echo "reboot" > "${DEVICE_PATH}"; sleep 10

		echo "uboot-by-usb-download" >> /opt/share/log.txt
		echo "$path" >> /opt/share/log.txt
		
		# android
		if [ "$path" == "result-navi_ref" ] || [ "$path" == "result-clova" ] || [ "$path" == "result-navi_ref_quickboot" ] || [ "$path" == "result-s5p4418-avn_ref" ] || [ "$path" == "result-s5p4418-avn_ref_quickboot" ] || [ "$path" == "result-s5p6818-avn_ref" ] || [ "$path" == "result-s5p6818-avn_ref_quickboot" ]; then
			/opt/share/$path/boot_by_usb.sh

		# yocto
		else
        	/opt/share/$path/tools/standalone-uboot-by-usb-download.sh
		fi

        for ((i=0;i<10;i++)); do
            echo " " > "${DEVICE_PATH}"
            sleep 0.1
        done
	
		# change serial name
		echo "setenv serial# ${path:7}" > "${DEVICE_PATH}"; sleep 5
		echo " " > "${DEVICE_PATH}"
		echo "setenv serial# ${path:7}" > "${DEVICE_PATH}"; sleep 5

		echo "boot" > "${DEVICE_PATH}"; sleep 15
        echo "root" > "${DEVICE_PATH}"; sleep 3
        echo "root" > "${DEVICE_PATH}"; sleep 3
        echo "root" > "${DEVICE_PATH}"; sleep 3
		sleep 15
		echo "/usr/bin/start_adbd.sh" > "${DEVICE_PATH}"; sleep 3
        echo "/usr/bin/start_adbd.sh" > "${DEVICE_PATH}"; sleep 3
        echo "/usr/bin/start_adbd.sh" > "${DEVICE_PATH}"; sleep 3
        echo "/usr/bin/start_adbd.sh" > "${DEVICE_PATH}"; sleep 3
        echo "/usr/bin/start_adbd.sh" > "${DEVICE_PATH}"; sleep 3
		echo " " > "${DEVICE_PATH}"
		echo "OKAY"
        echo "======================================="
        echo "Success, reset after fastboot download!"
        echo "======================================="

    elif [ "$command" == 'boot' ]; then
	echo " " > "${DEVICE_PATH}"; sleep 5
        echo "boot" > "${DEVICE_PATH}"; sleep 15

    elif [ "$command" == 'boot2' ]; then
    	echo "reset" > "${DEVICE_PATH}"; sleep 3
	cd /opt/share/$path
	/opt/share/$path/boot_by_usb.sh $path

    elif [ "$command" == 'boot3' ]; then
    	echo "reset" > "${DEVICE_PATH}"; sleep 3
	/opt/share/$path/tools/standalone-uboot-by-usb-download.sh

    else
        echo "finished"
    fi
}

function run_uboot_by_usb_download()
{     
    /opt/share/$1/tools/standalone-uboot-by-usb-download.sh
    for ((i=0;i<5;i++)); do
        sleep 0.5
        echo " " > "${DEVICE_PATH}"
    done
    echo "OKAY"
    echo "==================================="
    echo "Success, Nexell run-uboot download!"
    echo "==================================="
    
}

function run_fastboot_download()
{     
    /opt/share/$1/tools/standalone-fastboot-download.sh; sleep 3
    echo "OKAY"
    echo "=================================="
    echo "Success, Nexell Fastboot download!"
    echo "=================================="
}

run_command
