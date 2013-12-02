"""
Custom ZenPack initialization code. All code defined in this module will be
executed at startup time in all Zope clients.
"""

import logging
log = logging.getLogger('zen.ActiveMQ')

import Globals

from Products.ZenModel.Device import Device
from Products.ZenModel.ZenPack import ZenPack as ZenPackBase
from Products.ZenRelations.RelSchema import ToManyCont, ToOne
from Products.ZenUtils.Utils import unused
from Products.Zuul.interfaces import ICatalogTool


unused(Globals)


ZENPACK_NAME = 'ZenPacks.Eseye.ActiveMQ'

# Define new device relations.
# This is extending the existing object called Device (defined in $ZENHOME/Products/ZenModeler/Device.py)
# See ZenPacks.zenoss.OpenVZ - https://github.com/zenoss/ZenPacks.zenoss.OpenVZ as another example
#
# This is the simple way to add a single relationship
# The ActiveMQQueue object defined in ZenPacks.Eseye.ActiveMQ.ActiveMQQueue must have a matching 
#  relationship called activeMQServer that references back to this activeMQQueues relationship on
#    Products.ZenModel.Device.Device
#
# Device._relations += (('activeMQQueues', ToManyCont(ToOne,
#    'ZenPacks.Eseye.ActiveMQ.ActiveMQQueue.ActiveMQQueue', 'activeMQServer')), )



# If you want to define several new component types and relations, use the following structure
# NEW_DEVICE_RELATIONS is a tuple of tuples of ( relname, modname )
# NEW_COMPONENT_TYPES is a tuple of references to the object definitions of the new components
#
NEW_DEVICE_RELATIONS = (
    ('activeMQQueues', 'ActiveMQQueue'),
    )

NEW_COMPONENT_TYPES = (
    'ZenPacks.Eseye.ActiveMQ.ActiveMQQueue.ActiveMQQueue',
    )

# Add new relationships to Device if they don't already exist.
#
for relname, modname in NEW_DEVICE_RELATIONS:
    if relname not in (x[0] for x in Device._relations):
        Device._relations += (
            (relname, ToManyCont(ToOne,
                '.'.join((ZENPACK_NAME, modname)), 'activeMQServer')),
            )

# Add a new attribute to the Device object class
#
if not hasattr(Device, 'numMQQueues'):
    Device.numMQQueues = 0
    Device._properties += (
        {'id': 'numMQQueues', 'type': 'int', 'mode': 'w'},
        )




class ZenPack(ZenPackBase):
    """
    ZenPack loader that handles custom installation and removal tasks.
    """
    packZProperties = [
	('zActiveMQUser', 'admin', 'string'),
	('zActiveMQPassword', 'password', 'password'),
	('zActiveMQStompPort', 61613, 'int'),
	('zActiveMQStompSslPort', 61612, 'int'),
	('zActiveMQUseSsl', False, 'boolean')
    ]

    def install(self, app):
        super(ZenPack, self).install(app)

        log.info('Adding ActiveMQ relationships to existing devices')
        self._buildDeviceRelations()

    def remove(self, app, leaveObjects=False):
        if not leaveObjects:
            log.info('Removing ActiveMQ components')
            # Code to go with simple addition of single relationship
            #
            #cat = ICatalogTool(app.zport.dmd)
            #for brain in cat.search(types=('ZenPacks.Eseye.ActiveMQ.ActiveMQQueue.ActiveMQQueue')):
            #    component = brain.getObject()
            #    component.getPrimaryParent()._delObject(component.id)
            #
            #Device._relations = tuple(
            #    [x for x in Device._relations if x[0] != 'activeMQQueues'])


            #  If you are using the NEW_DEVICE_RELATIONS mechanism to specify several new relations
            #     use the following to remove all of them
            #
            cat = ICatalogTool(app.zport.dmd)
            for brain in cat.search(types=NEW_COMPONENT_TYPES):
                component = brain.getObject()
                component.getPrimaryParent()._delObject(component.id)

            # Need to get a list of just the relationship names - don't need modnames here
            relsOnly = []
            for relname, modname in NEW_DEVICE_RELATIONS:
                relsOnly.append(relname)

            Device._relations = tuple(
                [x for x in Device._relations \
                    if x[0] not in relsOnly])



            self._buildDeviceRelations()

        super(ZenPack, self).remove(app, leaveObjects=leaveObjects)


    def _buildDeviceRelations(self):
        for d in self.dmd.Devices.getSubDevicesGen():
            d.buildRelations()


