from Products.ZenRelations.RelSchema import ToManyCont, ToOne
from Products.ZenModel.Device import Device

class ActiveMQServer(Device):
	"""
	ActiveMQ Server Class
	"""

        # Note that the relationship ideally has a different name from the class to improve clarity

	_relations = Device._relations + (
		("activeMQQueues", ToManyCont(ToOne,
			"ZenPacks.Eseye.ActiveMQ.ActiveMQQueue", "activeMQServer")),
		)

        # Don't need any factory_type information - it will inherit basic stuff from the Device object class
	#factory_type_information = deepcopy(Device.factory_type_information)

