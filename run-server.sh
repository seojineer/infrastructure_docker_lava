#!/bin/bash

#docker run -it --name con_lava_server2 -p 9099:80 -p 5555:5555 -p 5556:5556 -h lava-server nexelldocker/lava-server
#docker run --net dockernet --ip 192.168.1.45 -d -it --name new_lava_server -p 9090:80 -p 5555:5555 -p 5556:5556 -h new_lava_server new_server
#docker run -itd --name new_lava_server -p 9090:5432 -p 5555:5555 -p 5556:5556 -h new_lava_server new_server
docker run -itd --name new_lava_server --cap-add=NET_ADMIN -p 192.168.1.44:8000:80 -p 5555:5555 -p 5556:5556 -h new_lava_server nexelldocker/lava-server
