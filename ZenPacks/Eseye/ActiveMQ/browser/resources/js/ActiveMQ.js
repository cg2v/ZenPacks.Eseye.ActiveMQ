(function() {
	var ZC = Ext.ns('Zenoss.component');

        /* the name following ZC. must exactly match the component name + Panel */
	ZC.ActiveMQQueuePanel = Ext.extend(ZC.ComponentGridPanel, {
			constructor: function(config) {
				config = Ext.applyIf(config||{}, {
					componentType: 'ActiveMQQueue',
                                        autoExpandColumn: 'QueueName',
					fields: [
                                        {name: 'uid'},
                                        {name: 'name'},
                                        {name: 'severity'},
					{name: 'QueueName'},
                                        {name: 'usesMonitorAttribute'},
                                        {name: 'monitor'},
                                        {name: 'monitored'},
                                        {name: 'locking'}
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
						width: 300
                                        },{
                                                dataIndex: 'monitored',
                                                header: _t('Monitored'),
                                                renderer: Zenoss.render.checkbox,
                                                sortable: true,
                                                width: 65
                                                    
					}]
				});
				ZC.ActiveMQQueuePanel.superclass.constructor.call(this, config);
			}
		});

	Ext.reg('ActiveMQQueuePanel', ZC.ActiveMQQueuePanel);
	ZC.registerName('ActiveMQQueue', _t('Queue'), _t('Queues'));


})();
