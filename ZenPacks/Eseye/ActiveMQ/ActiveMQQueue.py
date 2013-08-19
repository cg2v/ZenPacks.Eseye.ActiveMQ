from Globals import InitializeClass
from Products.ZenRelations.RelSchema import *
from Products.ZenModel.DeviceComponent import DeviceComponent
from Products.ZenModel.ManagedEntity import ManagedEntity
from Products.ZenModel.ZenossSecurity import ZEN_CHANGE_DEVICE

class ActiveMQQueue(DeviceComponent, ManagedEntity):
	"""
	ActiveMQ Queue Class
	"""

	portal_type = meta_type = 'ActiveMQQueue'
	
	QueueName = 'Unknown'

	_properties = ManagedEntity._properties + (
		{'id':'QueueName', 'type':'string', 'mode':'w'},
        )
	_relations = ManagedEntity._relations + (
        ("ActiveMQServer", ToOne(ToManyCont,
            "ZenPacks.Eseye.ActiveMQ.ActiveMQServer", "ActiveMQQueue")),
        )

	

	#This makes the "Templates" component display available.
	factory_type_information = (
		{
		'id': 'ActiveMQQueue',
		'meta_type': 'ActiveMQQueue',
		'description': """Serval Instance Info""",
		'product': 'ActiveMQ',
		'actions': ({
			'id': 'perfConf',
			'name': 'Template',
			'action': 'objTemplates',
			'permissions': (ZEN_CHANGE_DEVICE,),
			},),
		},)

	isUserCreatedFlag = True

	def isUserCreated(self):
		"""
		Returns the value of isUserCreated. True adds SAVE & CANCEL buttons to Details menu
		"""
		return self.isUserCreatedFlag

	def viewName(self):
		"""Pretty version human readable version of this object"""
		if self.QueueName == 'unknown':
			return "Unknown"
		else:
			#            return self.id
			return self.QueueName

	def primarySortKey(self):
		"""Sort by instance name"""
		return "%s" % (self.QueueName)

	def device(self):
		return self.ActiveMQServer()

	def monitored(self):
		"""
		If a bridge channel exists start monitoring it. Because channels are
		very dynamic we will just assume that they should be modeled if they
		exist. Of course the modeler would need to run very fequently to give
		accurate results as to who is talking at any given time. Looks like
		the default timeout on a cisco switch is 5 minutes so the modeler
		would need to run at about that frequency to keep this table accurate.
		If you increase the timeout you will get more accurate resuslts with a
		longer modeling cycle. The max time on a cisco box is 12 hours.
		"""
		return True

InitializeClass(ActiveMQQueue)
