import xmlrpc.client

username = "admin"
token = "4ztqijnjeyqc21f19rq766bdauueu7mbdddel436hp8278s7thp3z0pihsm4a2suj6b0ijupp3xq5wj4a49d6zyg207ws2blfsnqy4p83gzj6l32ktedo4e7ay5z7lo4"
#hostname = "lava-slave"
hostname = "192.168.1.44:8000"
protocol = "https"
#jinja_string = "/home/lava/lava-server/lava_scheduler_app/tests/devices/s5p4418-navi-ref-qt.jinja2"
jinja_string = "s5p4418-navi-ref-qt.jinja2"
#server = xmlrpc.client.ServerProxy("%s://%s:%s@%s/RPC2" % (protocol, username, token, hostname))
server = xmlrpc.client.ServerProxy("https://%s:%s@%s/RPC2" % (username, token, hostname), allow_none=True)
print(server.system.listMethods())
server.scheduler.import_device_dictionary("s5p4418-navi-ref-qt", jinja_string)
