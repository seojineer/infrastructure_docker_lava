#!/bin/bash

set -e

CURRENT_PATH=`dirname $0`
TOOLS_PATH=`readlink -ev $CURRENT_PATH`

argc=$#
TARGET_NAME=$1

function select_submit()
{
    cd ${TOOLS_PATH}/lavatest
 
    # yocto
    if [ "s5p4418-avn-ref-tiny" == ${TARGET_NAME} ]; then
        ./submit-nexell-testjob-s5p4418-avn-ref-tiny.sh
    elif [ "s5p4418-avn-ref-qt" == ${TARGET_NAME} ]; then
        ./submit-nexell-testjob-s5p4418-avn-ref-QT.sh
    elif [ "s5p4418-avn-ref-qt" == ${TARGET_NAME} ]; then
        ./submit-nexell-testjob-s5p4418-avn-ref-qt.sh
    elif [ "s5p4418-navi-ref-tiny" == ${TARGET_NAME} ]; then
        ./submit-nexell-testjob-s5p4418-navi-ref-tiny.sh
    elif [ "s5p4418-navi-ref-qt" == ${TARGET_NAME} ]; then
        ./submit-nexell-testjob-s5p4418-navi-ref-qt.sh
    elif [ "s5p4418-navi-ref-sato" == ${TARGET_NAME} ]; then
        ./submit-nexell-testjob-s5p4418-navi-ref-sato.sh
    elif [ "s5p4418-daudio-ref-qt" == ${TARGET_NAME} ]; then
        ./submit-nexell-testjob-s5p4418-daudio-ref-qt.sh
    elif [ "s5p6818-avn-ref-qt" == ${TARGET_NAME} ]; then
        ./submit-nexell-testjob-s5p6818-avn-ref-qt.sh

    # android
    elif [ "s5p4418-navi-ref" == ${TARGET_NAME} ]; then
        ./submit-nexell-testjob-s5p4418-navi-ref.sh
    elif [ "s5p4418-navi-ref-quickboot" == ${TARGET_NAME} ]; then
        ./submit-nexell-testjob-s5p4418-navi-ref-quickboot.sh

    elif [ "s5p4418-avn-ref" == ${TARGET_NAME} ]; then
        ./submit-nexell-testjob-s5p4418-avn-ref.sh
    elif [ "s5p4418-avn-ref-quickboot" == ${TARGET_NAME} ]; then
        ./submit-nexell-testjob-s5p4418-avn-ref-quickboot.sh

    elif [ "s5p6818-avn-ref" == ${TARGET_NAME} ]; then
        ./submit-nexell-testjob-s5p6818-avn-ref.sh
    elif [ "s5p6818-avn-ref-quickboot" == ${TARGET_NAME} ]; then
        ./submit-nexell-testjob-s5p6818-avn-ref-quickboot.sh

    elif [ "s5p4418-clova-ref" == ${TARGET_NAME} ]; then
        ./submit-nexell-testjob-s5p4418-clova-ref.sh
    else
        echo "TBD"
    fi
}

select_submit
