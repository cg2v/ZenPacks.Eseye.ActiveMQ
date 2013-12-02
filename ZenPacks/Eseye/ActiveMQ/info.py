from zope.interface import implements
from Products.Zuul.infos import ProxyProperty
from Products.Zuul.infos.component import ComponentInfo
from ZenPacks.Eseye.ActiveMQ import interfaces


class ActiveMQQueueInfo(ComponentInfo):
    implements(interfaces.IActiveMQQueueInfo)

    QueueName = ProxyProperty('QueueName')
