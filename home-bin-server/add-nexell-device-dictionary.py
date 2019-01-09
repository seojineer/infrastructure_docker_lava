import xmlrpc.client
import sys

username = "admin"
token = "bpexdhlth2sckkst1pslnklklw9enis92oe0ncqc4n7yby6mb5bxapof9ll503gqcqaq3rbq6o1765njgtydwozsjudur9bee8escj4zblqmbds0el0ud10qclbbn2hs"
hostname = "192.168.1.20:9099"
server = xmlrpc.client.ServerProxy("http://%s:%s@%s/RPC2" % (username, token, hostname), allow_none=True)

# qemu01
file = open('/home/lava/bin/nexell-device-dic/qemu01.jinja2','r')
jinja_string = file.read()
file.close()
server.scheduler.import_device_dictionary("qemu01", jinja_string)

# qemu02
#file = open('/home/lava/bin/nexell-device-dic/qemu02.jinja2','r')
#jinja_string = file.read()
#file.close()
#server.scheduler.import_device_dictionary("qemu02", jinja_string)

# imx8m
file = open('/home/lava/bin/nexell-device-dic/imx8m-01.jinja2','r')
jinja_string = file.read()
file.close()
server.scheduler.import_device_dictionary("imx8m-01", jinja_string)

# s5p4418-navi-ref-qt
file = open('/home/lava/bin/nexell-device-dic/s5p4418-navi-ref-qt.jinja2','r')
jinja_string = file.read()
file.close()
server.scheduler.import_device_dictionary("s5p4418-navi-ref-qt", jinja_string)

# s5p4418-navi-ref
file = open('/home/lava/bin/nexell-device-dic/s5p4418-navi-ref.jinja2','r')
jinja_string = file.read()
file.close()
server.scheduler.import_device_dictionary("s5p4418-navi-ref", jinja_string)
