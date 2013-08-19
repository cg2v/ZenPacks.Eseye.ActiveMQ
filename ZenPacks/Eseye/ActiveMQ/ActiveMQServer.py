from Globals import InitializeClass
from Products.ZenRelations.RelSchema import *
from Products.ZenModel.Device import Device
from copy import deepcopy

class ActiveMQServer(Device):
	"""
	ActiveMQ Server Class
	"""

	_relations = Device._relations + (
		("ActiveMQQueue", ToManyCont(ToOne,
			"ZenPacks.Eseye.ActiveMQ.ActiveMQQueue", "ActiveMQServer")),
		)

	factory_type_information = deepcopy(Device.factory_type_information)

	def __init__(self, *args, **kw):
		Device.__init__(self, *args, **kw)
		self.buildRelations()

InitializeClass(ActiveMQServer)
