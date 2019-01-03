#!/usr/bin/python
import argparse
import os.path
import sys
import time
import xmlrpclib

SLEEP = 5
__version__ = 0.5

LAVA_SERVER_IP = "192.168.1.20"

def is_valid_file(parser, arg, flag):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return open(arg, flag)  # return an open file handle


def setup_args_parser():
    """Setup the argument parsing.

    :return The parsed arguments.
    """
    description = "Submit job file"
    parser = argparse.ArgumentParser(version=__version__, description=description)
    parser.add_argument("yamlfile", help="specify target job file", metavar="FILE",
                   type=lambda x: is_valid_file(parser, x, 'r'))
    parser.add_argument("-d", "--debug", action="store_true", help="Display verbose debug details")
    parser.add_argument("-p", "--poll", action="store_true", help="poll job status until job completes")
    parser.add_argument("-k", "--apikey", default="apikey.txt", help="File containing the LAVA api key")
    parser.add_argument("--port", default="9099", help="LAVA/Apache default port number")

    return parser.parse_args()


def loadConfiguration():
    global args
    args = setup_args_parser()


def loadJob(server_str):
    """loadJob - read the JSON job file and fix it up for future submission
    """
    return args.yamlfile.read()


def submitJob(yamlfile, server):
    """submitJob - XMLRPC call to submit a JSON file

       returns jobid of the submitted job
    """
    # When making the call to submit_job, you have to send a string
    jobid = server.scheduler.submit_job(yamlfile)
    return jobid


def monitorJob(jobid, server, server_str):
    """monitorJob - added to poll for a job to complete

    """
    if args.poll:
        sys.stdout.write("Job polling enabled\n")
        # wcount = number of times we loop while the job is running
        wcount = 0
        # count = number of times we loop waiting for the job to start
        count = 0
		
	f = open("job_status.txt", "w+")

        while True:
            status = server.scheduler.job_status(jobid)
            if status['job_status'] == 'Complete':
		f.write("Complete\n")
                break
            elif status['job_status'] == 'Canceled':
		f.write("Canceled\n")
                print '\nJob Canceled'
                exit(0)
            elif status['job_status'] == 'Submitted':
                sys.stdout.write("Job waiting to run for % 2d seconds\n" % (wcount * SLEEP))
                sys.stdout.flush()
                wcount += 1
            elif status['job_status'] == 'Running':
                sys.stdout.write("Job Running for % 2d seconds\n" % (count * SLEEP))
                sys.stdout.flush()
                count += 1
            else:
		f.write("unkonwn status\n")
                print "unknown status"
                exit(0)
            time.sleep(SLEEP)
        print '\n\nJob Completed: ' + str(count * SLEEP) + ' s (' + str(wcount * SLEEP) + ' s in queue)'


def process():
    print "Submitting test job to LAVA server"
    loadConfiguration()
    user = "admin"
    with open(args.apikey) as f:
        line = f.readline()
        apikey = line.rstrip('\n')

    server_str = 'http://' + LAVA_SERVER_IP + ":" + args.port
    xmlrpc_str = 'http://' + user + ":" + apikey + "@" + LAVA_SERVER_IP + ":" + args.port + '/RPC2/'
    print server_str
    print xmlrpc_str
    server = xmlrpclib.ServerProxy(xmlrpc_str)
    server.system.listMethods()

    yamlfile = loadJob(server_str)

    jobid = submitJob(yamlfile, server)

    monitorJob(jobid, server, server_str)


if __name__ == '__main__':
    process()
