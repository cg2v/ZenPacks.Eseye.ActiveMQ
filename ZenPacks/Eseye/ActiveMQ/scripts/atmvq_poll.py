import re
import stomp, time
import json
import sys
import getopt

class MyListener(stomp.ConnectionListener):
	queues = {}
	#logger = None

	#def set_logger(self, log):
		#self.logger = log
		#log.info("logger added")

	def on_error(self, headers, message):
		print 'error: %s' % message

	def on_message(self, headers, message):
		#self.logger.info('on_message called!')
		#self.logger.info('%s' % message)
		json_message = message
		#print json_message
		jsonLoad = json.loads(json_message)
		queueName = jsonLoad['map']['entry'][5]["string"][1].replace("queue://", "")

		#Consumer Count is just that - how many consumers the queue has.
		consumerCount = jsonLoad['map']['entry'][9]["long"]

		#Queue Size in ActiveMQ Statistics is the number of messages currently in the queue.
		size = jsonLoad['map']['entry'][6]["long"]

		#enqueueCount is the total number of messages sent to this queue since the last broker restart.
		enqueueCount = jsonLoad['map']['entry'][14]["long"]

		if not re.search('ActiveMQ\.Statistics\.', queueName):
			#self.logger.info('queueid: %s' % queueName)
			#self.logger.info('%s' % queueName)
			#om = ObjectMap(data=dict(id=queueName, title=queueName), modname="ZenPacks.Eseye.ActiveMQ.ActiveMQQueue", classname="ActiveMQQueue")
			#self.queues.append(om)
			#for key,value in om.__dict__.items():
				#self.logger.info("OM Key: %s, OM Value: %s" % (key, value))
			self.queues[queueName] = [queueName, consumerCount, size, enqueueCount]
			#self.queues[queueName] = queueName
			#print queues
			return queueName
		else:
			#self.logger.info("Weird ActiveMQ.Statistics. queue returned from server")
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

def main(argv):

	user = "zenoss"
	password = "zenoss@eseye.comSecret"
	ipaddress = "192.168.243.8"
	component = ">"

	try:
		opts, args = getopt.getopt(argv, "hu:p:i:c:", ["help", "user=", "pass=", "ip=", "component="])
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

##################################### ENDOPTS

	queues = []

	conn = stomp.Connection([(ipaddress, 61613)], user, password)
	if conn:
		print 'Connection to %s successfully established' % ipaddress

	listener = MyListener()
	conn.set_listener('', listener)
	#listener.set_logger(log)
	#log.info('Listener added')

	conn.start()
	conn.connect(wait=True)
	conn.subscribe(destination='/temp-queue/ActiveMQ.Queues', ack='auto', transformation="jms-map-json", id="zenoss")

	#log.info("Subscribed to /temp-queue/ActiveMQ.Queues")
	dest = 'ActiveMQ.Statistics.Destination.%s' % (component)
	print dest
	conn.send("", destination=dest, headers={'reply-to':'/temp-queue/ActiveMQ.Queues'})

	time.sleep(10)

	conn.unsubscribe(id="zenoss")
	conn.disconnect()
	#log.info("Disconnected after timeout.")

	output = ""

	queues = listener.get_queues()
	if len(queues) > 0:
		#RETURN QUEUES FOR ADDITION TO ZODB
		#log.info('Queues: %d' % len(queues))
		for qid, qdetails in queues.items():
			print "\n" + qid
			print "Consumer count: %s, Queue size: %s, Enqueue Count: %s" % (qdetails[1], qdetails[2], qdetails[3])
	else:
		#ERROR
		#log.info('No queues found!')
		print "Error!"

if __name__ == "__main__":
	if len(sys.argv) > 1:
		main(sys.argv[1:])
	else:
		main(sys.argv)
