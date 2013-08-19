#ActiveMQDatasource
from collections import defaultdict

from zope.component import adapts
from zope.interface import implements

from Products.ZenModel.RRDDataSource import RRDDataSource
from Products.ZenModel.ZenPackPersistence import ZenPackPersistence
from Products.ZenUtils.ZenTales import talesEvalStr

from Products.Zuul.form import schema
from Products.Zuul.infos import ProxyProperty
from Products.Zuul.infos.template import RRDDataSourceInfo
from Products.Zuul.interfaces import IRRDDataSourceInfo
from Products.Zuul.utils import ZuulMessageFactory as _t


class ActiveMQDataSource(ZenPackPersistence, RRDDataSource):
	"""ActiveMQ data source."""

	#All ZenPackPersistence DataSources need to have ZENPACKID in them.
	ZENPACKID = 'ZenPacks.Eseye.ActiveMQCollector'

	#We only have a Python data source type.
	sourcetypes = ('ActiveMQ',)
	sourcetype = sourcetypes[0]

	plugin_classname = None

	# Defined instead of inherited to change cycletime type to string.
	# I don't really understand why this is necessary or even useful.
	_properties = (
		{'id': 'sourcetype', 'type': 'selection', 'select_variable': 'sourcetypes', 'mode': 'w'},
		{'id': 'enabled', 'type': 'boolean', 'mode': 'w'},
		{'id': 'component', 'type': 'string', 'mode': 'w'},
		{'id': 'eventClass', 'type': 'string', 'mode': 'w'},
		{'id': 'eventKey', 'type': 'string', 'mode': 'w'},
		{'id': 'severity', 'type': 'int', 'mode': 'w'},
		{'id': 'commandTemplate', 'type': 'string', 'mode': 'w'},
		{'id': 'cycletime', 'type': 'string', 'mode': 'w'},
		{'id': 'plugin_classname', 'type': 'string', 'mode': 'w'},
		)

	def getDescription(self):
		return self.plugin_classname

	def talesEval(self, text, context):
		device = context.device()
		extra = {
			'device': device,
			'dev': device,
			'devname': device.id,
			'datasource': self,
			'ds': self,
			}

		return talesEvalStr(str(text), context, extra=extra)

	def getCycleTime(self, context):
		return int(self.talesEval(self.cycletime, context))

	def getConfigKey(self, context):
		"""Returns a tuple to be used to split configs at the collector."""
		if not self.plugin_classname:
			return [context.id]

		from ZenPacks.Eseye.ActiveMQCollector.services.ActiveMQConfig \
			import load_plugin_class

		plugin_class = load_plugin_class(self.plugin_classname)
		return plugin_class.config_key(self, context)

	def getParams(self, context):
		"""Returns extra parameters needed for collecting this datasource."""
		if not self.plugin_classname:
			return {}

		from ZenPacks.Eseye.ActiveMQ.services.ActiveMQConfig \
			import load_plugin_class

		plugin_class = load_plugin_class(self.plugin_classname)
		return plugin_class.params(self, context)


class IActiveMQDataSourceInfo(IRRDDataSourceInfo):
	plugin_classname = schema.TextLine(title=_t(u'Plugin Class Name'))
	cycletime = schema.TextLine(title=_t(u'Cycle Time (seconds)'))


class ActiveMQDataSourceInfo(RRDDataSourceInfo):
	implements(IActiveMQDataSourceInfo)
	adapts(ActiveMQDataSource)

	testable = False

	plugin_classname = ProxyProperty('plugin_classname')
	cycletime = ProxyProperty('cycletime')


class ActiveMQDataSourcePlugin(object):
	"""Abstract base class for an ActiveMQDataSourcePlugin."""

	proxy_attributes = ()

	@classmethod
	def config_key(cls, datasource, context):
		"""
		Return list that is used to split configurations at the collector.

		This is a classmethod that is executed in zenhub. The datasource and
		context parameters are the full objects.
		"""
		return (
			context.device().id,
			datasource.getCycleTime(context),
			datasource.rrdTemplate().id,
			datasource.id,
			datasource.plugin_classname,
			)

	@classmethod
	def params(cls, datasource, context):
		"""
		Return params dictionary needed for this plugin.

		This is a classmethod that is executed in zenhub. The datasource and
		context parameters are the full objects.
		"""
		return {}

	def new_data(self):
		"""
		Return an empty data structure.

		Suitable for returning from on* methods.

		This data structure should emulate the source format defined in
		Products.ZenRRD.parsers.JSON.
		"""
		return {
			'values': defaultdict(dict),
			'events': [],
			}

	def collect(self, config):
		"""No default collect behavior. Must be implemented in subclass."""
		return NotImplementedError

	def onResult(self, result, config):
		"""Called first for success and error."""
		return result

	def onSuccess(self, result, config):
		"""Called only on success. After onResult, before onComplete."""
		return result

	def onError(self, result, config):
		"""Called only on error. After onResult, before onComplete."""
		return result

	def onComplete(self, result, config):
		"""Called last for success and error."""
		return result
