from Products.Zuul.form import schema
from Products.Zuul.interfaces.component import IComponentInfo
from Products.Zuul.utils import ZuulMessageFactory as _t

class IActiveMQQueueInfo(IComponentInfo):
	QueueName = schema.TextLine(title=_t(u"Queue"))
