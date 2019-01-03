import xmlrpc.client
import sys

username = "admin"
token = "4sooz0l6j4fltduhs02e7lj2tjzo0nl8dneq5zlwx6zs674gju6k96wd3jr1srr05f4h8uy1fobt001f2zre3hoq0eqo036rppggir1f0ky3d6fycwtcucp9gfis9hs5"
hostname = "192.168.1.20:9099"
server = xmlrpc.client.ServerProxy("http://%s:%s@%s/RPC2" % (username, token, hostname), allow_none=True)

# qemu01
file = open('/home/lava/bin/nexell-device-dic/qemu01.jinja2','r')
jinja_string = file.read()
file.close()
server.scheduler.import_device_dictionary("qemu01", jinja_string)

# qemu02
file = open('/home/lava/bin/nexell-device-dic/qemu02.jinja2','r')
jinja_string = file.read()
file.close()
server.scheduler.import_device_dictionary("qemu02", jinja_string)

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
