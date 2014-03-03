#!/usr/bin/env python
#
import sys
#import os
#sys.path.insert(1, os.path.abspath(sys.path[0] + "/../lib"))
import stomp, time
import sys
import getopt
import logging
logging.basicConfig()

from ZenPacks.Eseye.ActiveMQ.stomputil import AppListener
from ZenPacks.Eseye.ActiveMQ.amqutil import run_poll_loop

##################################### OPTS

def usage():
        print "-h | --help"
        print "-u USER | --user=USER"
        print "-p PASS | --pass=PASS"
        print "-i IP_ADDRESS | --ip=IP_ADDRESS"
        print "-c COMPONENT | --component=COMPONENT"
        print "--port=PORTNUM"
        print "--sslport=PORTNUM"
        print "--usessl=?"

def main(argv):

        user = ""
        password = ""
        ipaddress = ""
        component = ">"
        device = ""
        port=61613
        sslport=61612
        usessl=False

        try:
                opts, args = getopt.getopt(argv, "hu:p:i:c:d:", ["help", "user=", "pass=", "ip=", "component=", "device=", "port=", "sslport=", "usessl="])
        except getopt.GetoptError:
                usage()
                sys.exit(2)

        for opt, arg in opts:
                if opt in ("-h", "--help"):
                        usage()
                        sys.exit()
                if opt in ("-u", "--user"):
                        user = arg

                if opt in ("-p", "--password"):
                        password = arg

                if opt in ("-i", "--ip"):
                        ipaddress = arg

                if opt in ("-c", "--component"):
                        component = arg

                if opt in ("-d", "--device"):
                        device = arg
                if opt == "--port":
                        port=arg
                if opt == "--sslport":
                        sslport=arg
                if opt == "--usessl":
                        if arg == 'False':
                                usessl=False
                        else:
                                usessl=bool(arg)


##################################### ENDOPTS

        queues = {}

        conn = stomp.Connection([(ipaddress, sslport if usessl else port)],
				use_ssl=usessl)

        listener = AppListener()
        conn.set_listener('', listener)

        conn.start()
	conn.connect(wait=False, username=user, passcode=password)
	listener.wait(10)
	if not listener.ok():
		print "ACTIVEMQ ERROR: Cannot get connect to activemq"
		print listener.get_error_message()
		#sys.exit(2)
	(queues, ok, errmsg)=run_poll_loop(conn, listener, component)
	if not ok:
		print "ACTIVEMQ ERROR: Cannot get activemq statistics"
		print emsg
		sys.exit(2)

        if len(queues) > 0:
                #RETURN QUEUES FOR ADDITION TO ZODB
                for qid, qdetails in queues.items():
			#print "\n" + qid
			#print "Consumer count: %s, Queue size: %s, Enqueue Count: %s" % (qdetails[1], qdetails[2], qdetails[3])
                        #print "Failed to get data for queue %s in device %s | consumerCount=%s queueSize=%s enqueueCount=%s dequeueCount=%s" % (component, device, qdetails[1], qdetails[2], qdetails[3], qdetails[4])
			print "data for queue %s in device %s | consumerCount=%s queueSize=%s enqueueCount=%s dequeueCount=%s" % (qid, device, qdetails[1], qdetails[2], qdetails[3], qdetails[4])
			#time.sleep(1)
                        #sys.exit(0)
        else:
                #ERROR
		time.sleep(1)
                print "ERROR: 0 or less queues!"

        return True

if __name__ == "__main__":
        if len(sys.argv) > 1:
                main(sys.argv[1:])
        else:
                main(sys.argv)

