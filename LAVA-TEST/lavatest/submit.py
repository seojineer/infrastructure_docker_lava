import xmlrpc.client
import sys
import argparse

username = "admin"
token = "bpexdhlth2sckkst1pslnklklw9enis92oe0ncqc4n7yby6mb5bxapof9ll503gqcqaq3rbq6o1765njgtydwozsjudur9bee8escj4zblqmbds0el0ud10qclbbn2hs"
hostname = "192.168.1.20:9099"

# qemu01
#file = open('/home/lava-slave/LAVA-TEST/lavatest/qemu01.yaml','r')
#jinja_string = file.read()
#file.close()
#server.scheduler.submit_job(jinja_string)

def args_parser():
    """ args parser.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('job_file', help="job_file", type=str)

    return parser.parse_args()

def loadJob():
    args.yamlfile.read()

def process():
    print ("Submitting test job to LAVA server")
    global args
    args = args_parser()

    server = xmlrpc.client.ServerProxy("http://%s:%s@%s/RPC2" % (username, token, hostname), allow_none=True)
    #yamlfile = loadJob()
    file = open(args.job_file,'r')
    yamlfile = file.read()
    file.close()

    server.scheduler.submit_job(yamlfile)

process()
