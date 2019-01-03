#!/bin/bash

CACHE=$1
CACHE_OPTION=

if [ -z ${CACHE} ]; then
    echo "You are anything use option"
    read -p "Are you sure? " -n 1 -r
    echo    # (optional) move to a new line
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Default build cache use!"
    else
        exit 1
    fi
elif [ ${CACHE} == "no" ]; then
    echo "Default build cache use!"
elif [ ${CACHE} == "yes" ]; then
    CACHE_OPTION="--no-cache=true"
else
    echo "Error!!"
fi

docker image build ${CACHE_OPTION} -t nexelldocker/lava-server:2018.11 -f Dockerfile-server .
echo "---------------------------------------------------------------"
echo "---------------------------------------------------------------"
echo "---------------------------------------------------------------"
docker image build ${CACHE_OPTION} -t nexelldocker/lava-slave:2018.11 -f Dockerfile-slave .
