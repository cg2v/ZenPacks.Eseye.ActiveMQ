#!/usr/bin/env python
#
import logging
import re
import time
import json
import stomp

from Products.ZenModel.Device import Device
from Products.ZenUtils.ZenScriptBase import ZenScriptBase
from Products.DataCollector.plugins.CollectorPlugin import PythonPlugin
from Products.DataCollector.plugins.DataMaps import ObjectMap, RelationshipMap
from Products.ZenUtils.Utils import prepId

class ActiveMQMap(PythonPlugin):

	deviceProperties = PythonPlugin.deviceProperties + (
		'zActiveMQUser',
		'zActiveMQPassword',
		'zActiveMQStompPort',
		'zActiveMQStompSslPort',
		'zActiveMQUseSsl'
	)

        def collect(self, device, log):

                # the collect process is the mechanism for getting modeling (ie configuration) data
               # The data is returned in results which is automatically passed to the process method

                log.info('Modeler %s collecting queue info for ActiveMQ.' % device.id)

                print device

                ipaddress = device.manageIp
                log.info('%s' % ipaddress)
                user = getattr(device, 'zActiveMQUser', None)
                password = getattr(device, 'zActiveMQPassword', None)
                port=getattr(device, 'zActiveMQStompPort', 61613)
                sslport=getattr(device, 'zActiveMQStompSslPort', 61612)
                usessl=getattr('zActiveMQUseSsl', False)

                conn = stomp.Connection([(ipaddress, sslport if usessl else port)], use_ssl=usessl)
                if conn:
                        log.debug('Connection to %s successfully established' % ipaddress)
                listener = MyListener()
                conn.set_listener('', listener)
                listener.set_logger(log)
                #log.info('Listener added')
                conn.start()
                conn.connect(wait=True, username=user, passcode=password)
                conn.subscribe(destination='/temp-queue/ActiveMQ.Queues', ack='auto', transformation="jms-map-json", id="zenoss")

                #log.info("Subscribed to /temp-queue/ActiveMQ.Queues")
                conn.send(body="", destination='ActiveMQ.Statistics.Destination.>', headers={'reply-to':'/temp-queue/ActiveMQ.Queues'})

                time.sleep(10)
                conn.unsubscribe(id="zenoss")
                conn.disconnect()
               #log.info("Disconnected after timeout.")


                results = listener.get_queues()
                return results




	def process(self, device, results, log):
		log.info('Processing modeler results for %s collecting queue info for ActiveMQ.' % device.id)

		#print device

                # The number of queues is just the length of your results dictionary

		queues = results

		num_queues = len(queues)
                maps = []

                # Object map for the ActiveMQServer device itself
                if results:
                    log.info("Found some queues for %s \n" % (device.id))
                    om = self.objectMap()
   		    om.setHWTag = "Number of Queues = " + str(num_queues)
                    om.numMQQueues = num_queues

                    # Add our device object map to the maps list
                    maps.append(om)


                    # Now do the realtionship maps for each queue component


                    queuemaps = []
                    for qid, qname in queues.items():
                        queuemaps.append(ObjectMap({
                           'id': self.prepId(qid),
                           'title': qname,
                           'QueueName': qname,
                            }))
                        #log.info(' queuemaps om is %s \n' % (queuemaps))
                    maps.append(RelationshipMap(
                    relname='activeMQQueues',
                    modname='ZenPacks.Eseye.ActiveMQ.ActiveMQQueue',
                    objmaps=queuemaps))

                    log.info(' queuemaps om is %s \n' % (queuemaps))
                    return maps

		else:
		    #ERROR
		    log.info('No queues found!')
		    return None




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

