import xmlrpc.client
import sys

username = "admin"
token = "bpexdhlth2sckkst1pslnklklw9enis92oe0ncqc4n7yby6mb5bxapof9ll503gqcqaq3rbq6o1765njgtydwozsjudur9bee8escj4zblqmbds0el0ud10qclbbn2hs"
hostname = "192.168.1.20:9099"
server = xmlrpc.client.ServerProxy("http://%s:%s@%s/RPC2" % (username, token, hostname), allow_none=True)

def dic_update(device_name):
    file = open('/home/lava/bin/nexell-device-dic/' + str(device_name) + '.jinja2','r')
    jinja_string = file.read()
    file.close()
    server.scheduler.import_device_dictionary(device_name, jinja_string)

dic_update('qemu01')
dic_update('qemu02')
dic_update('s5p4418-navi-ref-qt')
dic_update('s5p4418-navi-ref-tiny')
dic_update('s5p4418-navi-ref')
