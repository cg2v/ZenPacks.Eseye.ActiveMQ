import logging
import re
import stomp, time
import json

from Products.ZenModel.Device import Device
from Products.ZenUtils.ZenScriptBase import ZenScriptBase
from Products.DataCollector.plugins.CollectorPlugin import PythonPlugin
from Products.DataCollector.plugins.DataMaps import ObjectMap, RelationshipMap
from Products.ZenUtils.Utils import prepId

class ActiveMQServer(PythonPlugin):

	def collect(self, device, log):
		log.debug('ActiveMQServer modeler perceived')
		return True

	def process(self, device, results, log):
		log.info('Modeler %s collecting queue info for ActiveMQ.' % device.id)

		print device
		queues = []

		ipaddress = device.manageIp
		log.info('%s' % ipaddress)
		#user = device.zActiveMQUser
		#password = device.zActiveMQPassword
		user = "zenoss"
		password = "zenoss@eseye.comSecret"

		conn = stomp.Connection([(ipaddress, 61613)], user, password)
		if conn:
			log.debug('Connection to %s successfully established' % ipaddress)
		listener = MyListener()
		conn.set_listener('', listener)
		listener.set_logger(log)
		#log.info('Listener added')
		conn.start()
		conn.connect(wait=True)
		conn.subscribe(destination='/temp-queue/ActiveMQ.Queues', ack='auto', transformation="jms-map-json", id="zenoss")

		#log.info("Subscribed to /temp-queue/ActiveMQ.Queues")
		conn.send("", destination='ActiveMQ.Statistics.Destination.>', headers={'reply-to':'/temp-queue/ActiveMQ.Queues'})

		time.sleep(5)
		conn.unsubscribe(id="zenoss")
		conn.disconnect()
		#log.info("Disconnected after timeout.")

		num_queues = 0
		rm = self.relMap()
		rm.relname = "ActiveMQServer"
		rm.modname = "ZenPacks.Eseye.ActiveMQ.ActiveMQServer"

		queues = listener.get_queues()
		if len(queues) > 0:
			#RETURN QUEUES FOR ADDITION TO ZODB
			log.info('Queues: %d' % len(queues))
			for q in queues:
				num_queues = num_queues + 1
			om = self.objectMap(queues)
			om.setHWTag = "Number of Queues = " + str(num_queues)
			rm.append(om)
			return rm
		else:
			#ERROR
			log.info('No queues found!')
			return None


### IS THIS WORKING?
class MyListener(stomp.ConnectionListener):
	queues = {}
	logger = None

	def set_logger(self, log):
		self.logger = log
		#log.info("logger added")

	def on_error(self, headers, message):
		print 'error: %s' % message

	def on_message(self, headers, message):
		#self.logger.info('on_message called!')
		#self.logger.info('%s' % message)
		json_message = message
		jsonLoad = json.loads(json_message)
		queueName = jsonLoad['map']['entry'][5]["string"][1].replace("queue://", "")

		if not re.search('ActiveMQ\.Statistics\.', queueName):
			#self.logger.info('queueid: %s' % queueName)
			#self.logger.info('%s' % queueName)
			self.queues[queueName] = queueName
			return queueName
		else:
			#self.logger.info("Weird ActiveMQ.Statistics. queue returned from server")
			return None

	def get_queues(self):
		return self.queues
###
