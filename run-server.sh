#!/bin/bash

docker run -itd --name new_lava_server --cap-add=NET_ADMIN -p 80:80 -p 5557:5555 -p 5558:5556 -p 5500:5500 -h new_lava_server nexelldocker/lava-server:2018.11

