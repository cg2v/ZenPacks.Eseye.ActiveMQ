from zope.interface import implements
from zope.component import adapts
from Products.Zuul.infos import ProxyProperty
from Products.Zuul.infos.component import ComponentInfo
from ZenPacks.Eseye.ActiveMQ import interfaces
from ZenPacks.Eseye.ActiveMQ.ActiveMQQueue import ActiveMQQueue


class ActiveMQQueueInfo(ComponentInfo):
    implements(interfaces.IActiveMQQueueInfo)
    adapts(ActiveMQQueue)

    QueueName = ProxyProperty('QueueName')
