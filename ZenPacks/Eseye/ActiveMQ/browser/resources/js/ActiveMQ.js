(function() {
	var ZC = Ext.ns('Zenoss.component');

	ZC.QueueGridPanel = Ext.extend(ZC.ComponentGridPanel, {
			constructor: function(config) {
				config = Ext.applyIf(config||{}, {
					autoExpandColumn: 'QueueName',
					componentType: 'ActiveMQQueue',
					fields: [
					{name: 'QueueName'},
					{name: 'severity'},
					],
					columns: [{
						id: 'severity',
						dataIndex: 'severity',
						header: _t('Events'),
						renderer: Zenoss.render.severity,
						width: 60
					},{
						id: 'QueueName',
						dataIndex: 'QueueName',
						header: _t('Queue Name'),
						sortable: true,
						width: 150
					}]
				});
				ZC.QueueGridPanel.superclass.constructor.call(this, config);
			}
		});

	Ext.reg('QueueGridPanel', ZC.QueueGridPanel);
	ZC.registerName('ActiveMQQueue', _t('Queue'), _t('Queues'));

	Zenoss.nav.appendTo('Components', [{
		id: 'component_queues',
		text: _t('ActiveMQ Queues'),
		xtype: 'QueueGridPanel',
		subComponentGridPanel: true,
		filterNav: true,
		setContext: function(uid) {
			ZC.QueueGridPanel.superclass.setContext.apply(this, [uid]);
		}
	}]);

})();
