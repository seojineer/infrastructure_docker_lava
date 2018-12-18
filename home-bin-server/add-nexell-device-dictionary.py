import xmlrpc.client
import sys

username = "admin"
token = "f2a1dn4lg23e57wiaky1uwno27dmfqrdi2bqmhwismgbguof5dihmqdirnt10f0pr0n07h161a95ajdh0pchnc3oqzuar535ztouxg3ooktub80f44sd61rxre6n9pr2"
hostname = "192.168.1.44:9099"
server = xmlrpc.client.ServerProxy("http://%s:%s@%s/RPC2" % (username, token, hostname), allow_none=True)

# s5p4418-navi-ref-qt
file = open('/home/lava/lava-server/lava_scheduler_app/tests/devices/s5p4418-navi-ref-qt.jinja2','r')
jinja_string = file.read()
file.close()
server.scheduler.import_device_dictionary("s5p4418-navi-ref-qt", jinja_string)
