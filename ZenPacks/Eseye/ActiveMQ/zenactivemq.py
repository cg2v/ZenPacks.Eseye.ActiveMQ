#zendaemon
import logging
log = logging.getLogger('zen.ActiveMQ')

import Globals
import zope.component
import zope.interface

from twisted.internet import defer

from Products.ZenCollector.daemon import CollectorDaemon
from Products.ZenCollector.interfaces \
    import ICollectorPreferences, IScheduledTask, IEventService, IDataService

from Products.ZenCollector.tasks \
    import SimpleTaskFactory, SimpleTaskSplitter, TaskStates

from Products.ZenUtils.observable import ObservableMixin

# unused is way to keep Python linters from complaining about imports that we
# don't explicitely use. Occasionally there is a valid reason to do this.
from Products.ZenUtils.Utils import unused

# We must import our ConfigService here so zenhub will allow it to be
# serialized and deserialized. We'll declare it unused to satisfy linters.
from ZenPacks.Eseye.ActiveMQ.services.ActiveMQConfigService \
    import ActiveMQConfigService

unused(Globals)
unused(ActiveMQConfigService)


# Your implementation of ICollectorPreferences is where you can handle custom
# command line (or config file) options and do global configuration of the
# daemon.
class ActiveMQPreferences(object):
    zope.interface.implements(ICollectorPreferences)

    def __init__(self):
        self.collectorName = 'zenactivemq'
        self.configurationService = \
            "ZenPacks.Eseye.ActiveMQ.services.ActiveMQConfigService"

        # How often the daemon will collect each device. Specified in seconds.
        self.cycleInterval = 5 * 60 # 5 minutes

        # How often the daemon will reload configuration. In seconds.
        self.configCycleInterval = 60 * 60 * 12 # 12 hours

        self.options = None

    def buildOptions(self, parser):
        """
        Required to implement the ICollectorPreferences interface.
        """
        pass

    def postStartup(self):
        """
        Required to implement the ICollectorPreferences interface.
        """
        pass


# The implementation of IScheduledTask for your daemon is usually where most
# of the work is done. This is where you implement the specific logic required
# to collect data.
class ActiveMQTask(ObservableMixin):
    zope.interface.implements(IScheduledTask)

    STATE_FETCH_DATA = 'FETCH_DATA'
    STATE_STORE_PERF = 'STORE_PERF_DATA'

    def __init__(self, taskName, deviceId, interval, taskConfig):
        super(ActiveMQTask, self).__init__()
        self._taskConfig = taskConfig

        self._eventService = zope.component.queryUtility(IEventService)
        self._dataService = zope.component.queryUtility(IDataService)
        self._preferences = zope.component.queryUtility(
            ICollectorPreferences, 'activemq_daemon')

        # All of these properties are required to implement the IScheduledTask
        # interface.
        self.name = taskName
        self.configId = deviceId
        self.interval = interval
        # Any new Task created HAS to start in STATE_IDLE!
        self.state = TaskStates.STATE_IDLE

    # doTask is where the collector logic should go. It is also required to
    # implement the IScheduledTask interface. It will be called directly by the
    # framework when it's this task's turn to run.
    def doTask(self):
        # This method must return a deferred because the collector framework
        # is asynchronous.

        # That is so that the task waits until the Deferred has completed before proceeding.

        # I have no idea where the methods `add__` are coming from.
        d = self.plugin.collect(self.config)
        d.addBoth(self.plugin.onResult, self.config)
        d.addCallback(self.plugin.onSuccess, self.config)
        d.addErrback(self.plugin.onError, self.config)
        d.addBoth(self.plugin.onComplete, self.config)
        d.addCallback(self.processResults)
        d.addErrback(self.handleError)
        return d

    def processResults(self, result):
        self.sendEvents(result['events'])
        self.storeValues(result['values'])

    def sendEvents(self, events):
        if len(events) < 1:
            return

        # Default event fields.
        for event in events:
            event.setdefault('device', self.configId)
            event.setdefault('severity', ZenEventClasses.Info)

        self._eventService.sendEvents(events)

    def storeValues(self, values):
        self.state = ActiveMQCollectionTask.STATE_STORE_PERF

        for datasource in self.config.datasources:
            component_values = values.get(datasource.component)
            if not component_values:
                continue

            for dp_id, dp_value in component_values.items():
                for dp in datasource.points:
                    if dp.id != dp_id:
                        continue

                    threshData = {
                        'eventKey': datasource.getEventKey(dp),
                        'component': datasource.component,
                        }

                    self._dataService.writeRRD(
                        dp.rrdPath,
                        dp_value[0],
                        dp.rrdType,
                        rrdCommand=dp.rrdCreateCommand,
                        cycleTime=datasource.cycletime,
                        min=dp.rrdMin,
                        max=dp.rrdMax,
                        threshEventData=threshData,
                        timestamp=dp_value[1],
                        allowStaleDatapoint=False)

    def handleError(self, result):
        log.error('unhandled plugin error: %s', result)

    # cleanup is required to implement the IScheduledTask interface.
    def cleanup(self):
        pass


if __name__ == '__main__':
    myPreferences = ActiveMQPreferences()
    myTaskFactory = SimpleTaskFactory(ActiveMQTask)
    myTaskSplitter = SimpleTaskSplitter(myTaskFactory)

    daemon = CollectorDaemon(myPreferences, myTaskSplitter)
    daemon.run()
