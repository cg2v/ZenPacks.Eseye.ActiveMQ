from Globals import InitializeClass
from Products.ZenRelations.RelSchema import ToManyCont, ToOne
from Products.ZenModel.DeviceComponent import DeviceComponent
from Products.ZenModel.ManagedEntity import ManagedEntity
from Products.ZenModel.ZenossSecurity import ZEN_CHANGE_DEVICE

class ActiveMQQueue(DeviceComponent, ManagedEntity):
	"""
	ActiveMQ Queue Class
	"""

	portal_type = meta_type = 'ActiveMQQueue'

        # Disambiguate multi-inheritence.
        _properties = ManagedEntity._properties
        _relations = ManagedEntity._relations
    
	
	QueueName = 'Unknown'

	_properties = ManagedEntity._properties + (
		{'id':'QueueName', 'type':'string', 'mode':'w'},
        )
	_relations = ManagedEntity._relations + (
        ("activeMQServer", ToOne(ToManyCont,
            "Products.ZenModel.Device.Device", "activeMQQueues")),
        )

	
        # This makes the "Templates" component display available.
        factory_type_information = ({
            'actions': ({
                'id': 'perfConf',
                'name': 'Template',
                'action': 'objTemplates',
                'permissions': (ZEN_CHANGE_DEVICE,),
                },),
            },)
    
        # Query for events by id instead of name.
        event_key = "ComponentId"


        #  This is necessary - returns the device that contains this component
        #     by following the relationship on this component ( activeMQServer )

	def device(self):
		return self.activeMQServer()

        def name(self):
                return self.id

        # Don't think this is strictly necessary but a good convention
        def getRRDTemplateName(self):
            return 'ActiveMQQueue'


