#!/usr/bin/env python
#
import re
import stomp, time
import json
import sys
import getopt
import logging
logging.basicConfig()
class MyListener(stomp.ConnectionListener):
        queues = {}

        def on_error(self, headers, message):
                print 'error: %s' % message

        def on_message(self, headers, message):
                json_message = message
                #print json_message
                jsonLoad = json.loads(json_message)
		#print jsonLoad
                queueName = jsonLoad['map']['entry'][5]["string"][1].replace("queue://", "")

                #Consumer Count is just that - how many consumers the queue has.
                consumerCount = jsonLoad['map']['entry'][9]["long"]

                #Queue Size in ActiveMQ Statistics is the number of messages currently in the queue.
                size = jsonLoad['map']['entry'][6]["long"]

                #enqueueCount is the total number of messages sent to this queue since the last broker restart.
                enqueueCount = jsonLoad['map']['entry'][14]["long"]
		dequeueCount = jsonLoad['map']['entry'][1]["long"]

                if not re.search('ActiveMQ\.Statistics\.', queueName):
                        self.queues[queueName] = [queueName, consumerCount, size, enqueueCount, dequeueCount]
                        return queueName
                else:
                        return None

        def get_queues(self):
                return self.queues

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

        queues = []

        conn = stomp.Connection([(ipaddress, sslport if usessl else port)],
				use_ssl=usessl)

        listener = MyListener()
        conn.set_listener('', listener)

        conn.start()
	conn.connect(wait=True, username=user, passcode=password)
        conn.subscribe(destination='/temp-queue/ActiveMQ.Queues', ack='auto', transformation="jms-map-json", id="zenoss")

        dest = 'ActiveMQ.Statistics.Destination.%s' % (component)
        conn.send(body="", destination=dest, headers={'reply-to':'/temp-queue/ActiveMQ.Queues'})

        time.sleep(10)

        conn.unsubscribe(id="zenoss")
        conn.disconnect()

        output = ""

        queues = listener.get_queues()
        if len(queues) > 0:
                #RETURN QUEUES FOR ADDITION TO ZODB
                for qid, qdetails in queues.items():
                        print "Failed to get data for queue %s in device %s | consumerCount=%s queueSize=%s enqueueCount=%s dequeueCount=%s" % (component, device, qdetails[1], qdetails[2], qdetails[3], qdetails[4])
			time.sleep(1)
                        sys.exit(0)
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

