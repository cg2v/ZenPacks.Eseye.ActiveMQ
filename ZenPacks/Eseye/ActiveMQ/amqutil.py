# code for parsing activemq statistics responses
# Copyright (C) 2014 Chaskiel Grundman
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import uuid
import time
import re
import json
import logging
def map_to_dict(map):
        ret={}
        for e in map['map']['entry']:
                if len(e['string']) == 2:
                        ret[e['string'][0]]=e['string'][1]
                elif e.has_key('int'):
                        ret[e['string']]=int(e['int'])
                elif e.has_key('long'):
                        ret[e['string']]=long(e['long'])
                elif e.has_key('double'):
                        ret[e['string']]=float(e['double'])
                else:
                        raise ValueError("Unknown type for {0}".format(e['string']))
        return ret


def run_poll_loop(conn, listener, component, timer=10, logger=logging):
    queues={}
    subrecpt=str(uuid.uuid4())
    listener.prepare_wait(subrecpt)
    conn.subscribe(destination='/temp-queue/ActiveMQ.Queues', ack='auto',
                   transformation="jms-map-json", id="zenoss", receipt=subrecpt)
    listener.wait(10)
    if not listener.ok():
        return (queues, listener.ok(), listener.get_error_message())
    dest = 'ActiveMQ.Statistics.Destination.%s' % (component)
    conn.send(body="", destination=dest, headers={'reply-to':'/temp-queue/ActiveMQ.Queues'})
    et=time.time()+timer
    subcomplete=False
    while et > time.time():
        listener.wait(et-time.time())
        gotrecpt=listener.lastwaitfor()
        if subrecpt==gotrecpt:
            subcomplete=True
        if not listener.ok():
            break
        m=listener.get_message()
        if m:
            (headers, message)=m
            try:
                jsonLoad=json.loads(message)
                data=map_to_dict(jsonLoad)
                
                
                queueName = data['destinationName'].replace("queue://", "")
                #Consumer Count is just that - how many consumers the queue has.
                consumerCount = data['consumerCount']
                #Queue Size in ActiveMQ Statistics is the number of messages currently in the queue.
                size = data['size']
                #enqueueCount is the total number of messages sent to this queue since the last broker restart.
                enqueueCount = data['enqueueCount']
                dequeueCount = data['dequeueCount']
                if not re.search('ActiveMQ\.Statistics\.', queueName):
                    queues[queueName] = [queueName, consumerCount, size, enqueueCount, dequeueCount]
                    if queueName == component:
                        break
            except (KeyError, ValueError) as e:
                logger.exception("JSON Processing error")
                return (queues, False, "Bad data: " + e)
            except:
                logger.exception("Unexpected exception processing message")
                raise
    ok=listener.ok()
    emsg=listener.get_error_message()
    if subcomplete and conn.is_connected():
        conn.unsubscribe(id="zenoss")
    if conn.is_connected:
        conn.disconnect()
    return (queues, ok, emsg)
    
