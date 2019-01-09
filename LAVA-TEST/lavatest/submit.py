import xmlrpc.client
import sys
import argparse

username = "admin"
token = "bpexdhlth2sckkst1pslnklklw9enis92oe0ncqc4n7yby6mb5bxapof9ll503gqcqaq3rbq6o1765njgtydwozsjudur9bee8escj4zblqmbds0el0ud10qclbbn2hs"
hostname = "192.168.1.20:9099"

def args_parser():
    """ args parser.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('job_file', help="job_file", type=argparse.FileType('r'))

    return parser.parse_args()

def loadJob():
    return args.job_file.read()

def process():
    print ("Submitting test job to LAVA server")
    global args
    args = args_parser()

    server = xmlrpc.client.ServerProxy("http://%s:%s@%s/RPC2" % (username, token, hostname), allow_none=True)
    yamlfile = loadJob()
    #print(yamlfile)

    server.scheduler.submit_job(yamlfile)

process()
