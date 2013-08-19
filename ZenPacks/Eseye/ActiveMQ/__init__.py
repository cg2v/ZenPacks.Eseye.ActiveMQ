"""
Custom ZenPack initialization code. All code defined in this module will be
executed at startup time in all Zope clients.
"""

import logging
log = logging.getLogger('zen.ActiveMQ')

import Globals

from Products.ZenEvents.EventManagerBase import EventManagerBase
from Products.ZenModel.Device import Device
from Products.ZenModel.ZenPack import ZenPack as ZenPackBase
from Products.ZenRelations.RelSchema import ToManyCont, ToOne
from Products.ZenUtils.Utils import unused
from Products.Zuul.interfaces import ICatalogTool

unused(Globals)


ZENPACK_NAME = 'ZenPacks.Eseye.ActiveMQ'

# Define new device relations.
NEW_DEVICE_RELATIONS = (
    ('ActiveMQQueue', 'ActiveMQQueue'),
    )

NEW_COMPONENT_TYPES = (
    'ZenPacks.Eseye.ActiveMQ.ActiveMQQueue.ActiveMQQueue',
    )

# Add new relationships to Device if they don't already exist.
for relname, modname in NEW_DEVICE_RELATIONS:
    if relname not in (x[0] for x in Device._relations):
        Device._relations += (
            (relname, ToManyCont(ToOne,
                '.'.join((ZENPACK_NAME, modname)), 'ActiveMQServer')),
            )


class ZenPack(ZenPackBase):
    """
    ZenPack loader that handles custom installation and removal tasks.
    """

    def install(self, app):
        self.pre_install(app)
        super(ZenPack, self).install(app)

        log.info('Adding ActiveMQ relationships to existing devices')
        self._buildDeviceRelations()

    def pre_install(self, app):
         #Remove the "Throughput - Messages" graph so it can be replaced with
         #the proper packets graph from objects.xml.
        node_template = app.zport.dmd.Devices.rrdTemplates._getOb(
            'ActiveMQQueue', None)

        if node_template:
            messages_graph = node_template.graphDefs._getOb(
                'Throughput - Messages', None)

            if messages_graph:
                node_template.graphDefs._delObject(messages_graph.id)

    def remove(self, app, leaveObjects=False):
        if not leaveObjects:
            log.info('Removing ActiveMQ components')
            cat = ICatalogTool(app.zport.dmd)
            for brain in cat.search(types=NEW_COMPONENT_TYPES):
                component = brain.getObject()
                component.getPrimaryParent()._delObject(component.id)

            # Remove our Device relations additions.
            Device._relations = tuple(
                [x for x in Device._relations \
                    if x[0] not in NEW_DEVICE_RELATIONS])

            log.info('Removing ActiveMQ device relationships')
            self._buildDeviceRelations()

        super(ZenPack, self).remove(app, leaveObjects=leaveObjects)

    def _buildDeviceRelations(self):
        for d in self.dmd.Devices.getSubDevicesGen():
            d.buildRelations()


#We need to filter ActiveMQ components by id instead of name.
EventManagerBase.ComponentIdWhere = (
    "\"(device = '%s' and component = '%s')\""
    " % (me.device().getDmdKey(), me.id)")
