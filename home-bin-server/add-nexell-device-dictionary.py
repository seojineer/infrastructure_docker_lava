import xmlrpc.client
import sys

username = "admin"
token = "rl034q0tw089k2zdf257us9q80x5n72lw5q5rbdq80ucjz324qjb4kk1tdj3irs7qufy8bses68qz6boxgqytgu4g7l53ka057ud0wlmqomtbxed0p0k96ebf7qkk42f"
hostname = "192.168.1.20"
server = xmlrpc.client.ServerProxy("http://%s:%s@%s/RPC2" % (username, token, hostname), allow_none=True)

def dic_update(device_name):
    file = open('/home/lava/bin/nexell-device-dic/' + str(device_name) + '.jinja2','r')
    jinja_string = file.read()
    file.close()
    server.scheduler.import_device_dictionary(device_name, jinja_string)

dic_update('qemu01')
dic_update('qemu02')
dic_update('s5p4418-navi-ref-qt')
dic_update('s5p4418-navi-ref')
dic_update('s5p4418-navi-ref-ubuntu')
dic_update('s5p6818-avn-ref')
dic_update('s5p4418-convergence-svmc')
