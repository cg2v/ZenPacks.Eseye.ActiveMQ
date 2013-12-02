import logging
import re
import stomp, time
import json

from Products.ZenModel.Device import Device
from Products.ZenUtils.ZenScriptBase import ZenScriptBase
from Products.DataCollector.plugins.CollectorPlugin import PythonPlugin
from Products.DataCollector.plugins.DataMaps import ObjectMap, RelationshipMap
from Products.ZenUtils.Utils import prepId

class ActiveMQQueue(PythonPlugin):

	relname = "ActiveMQQueue"
	modname = "ZenPacks.Eseye.ActiveMQ.ActiveMQQueue"

	def collect(self, device, log):
		log.debug('ActiveMQQueue modeler perceived')
		return True

	def process(self, device, results, log):
		log.info('Modeler %s collecting queue info for ActiveMQ.' % self.name())

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
		log.info('Listener added')
		conn.start()
		conn.connect(wait=True)
		conn.subscribe(destination='/temp-queue/ActiveMQ.Queues', ack='auto', transformation="jms-map-json", id="zenoss")

		log.info("Subscribed to /temp-queue/ActiveMQ.Queues")
		conn.send("", destination='ActiveMQ.Statistics.Destination.>', headers={'reply-to':'/temp-queue/ActiveMQ.Queues'})

		time.sleep(10)
		conn.unsubscribe(id="zenoss")
		conn.disconnect()
		log.info("Disconnected after timeout.")

		rm = self.relMap()
		rm.relname = "ActiveMQQueue"
		rm.modname = "ZenPacks.Eseye.ActiveMQ.ActiveMQQueue"

		queues = listener.get_queues()
		log.info("%s", queues)
		if len(queues) > 0:
			#RETURN QUEUES FOR ADDITION TO ZODB
			log.info('Queues: %d' % len(queues))
			for qid, qname in queues.items():
				om = self.objectMap()
				om.id = prepId(qid)
				om.title = qname
				om.classname = "ActiveMQQueue"
				for key,value in om.__dict__.items():
					log.info("OM Key: %s, OM Value: %s" % (key, value))
				rm.append(om)
			log.info("RelationshipMap: %s", rm)
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
		log.info("logger added")

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
			self.logger.info('%s' % queueName)
			#om = ObjectMap(data=dict(id=queueName, title=queueName), modname="ZenPacks.Eseye.ActiveMQ.ActiveMQQueue", classname="ActiveMQQueue")
			#self.queues.append(om)
			#for key,value in om.__dict__.items():
				#self.logger.info("OM Key: %s, OM Value: %s" % (key, value))
			self.queues[queueName] = queueName
			return queueName
		else:
			self.logger.info("Weird ActiveMQ.Statistics. queue returned from server")
			return None

	def get_queues(self):
		return self.queues
###
