import xmlrpc.client
import sys

username = "admin"
token = "56h8gczfirmax1ap5cbkkncec0jt6qhbebohz4n4mxlst6e32p5quaoiurm45mhx36fnfdxubczfir7jtq23zxzpznk20u80j8da2uz5plgp4ejjz2z8z1ac60gh3jh8"
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
dic_update('s5p4418-navi-ref-tiny')
dic_update('s5p4418-navi-ref')
dic_update('s5p4418-convergence-svmc')
dic_update('s5p6818-avn-ref')
