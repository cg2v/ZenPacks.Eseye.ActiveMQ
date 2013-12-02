# README

## DEPENDENCIES

`stomp.py` (python library for STOMP communication with ActiveMQ)<br/>
`pythonssl` (stomp.py dep. - included in Zenoss environment)

## INSTALLATION - stomp.py

This release supports version 4.0 of stomp.py and does not work with earlier versions. Version 4.0.5 or newer is recommended.

To install, there are a few steps. Because the Python environment for Zenoss __is not__ the same as for the system, you cannot install `stomppy` with an _.RPM_ package, as this would install it for the system environment. You must install `stomppy` manually as the Zenoss user.

To download the _.RPM_ file, go [here](https://github.com/jasonrbriggs/stomp.py/releases) and download the __version 4.0.5__ _.tar.gz_. You will then need to upload it to your zenoss server.

Un-tar the file by running `tar -zxvf stomp.py-4.0.5.tar.gz` and then move the resulting file to a temporary folder in the zenoss home folder. This could be a sequence of instructions to follow:

	sudo su
	tar -zxvf stomp.py-4.0.5.tar.gz
	mkdir /opt/zenoss/local
	mv stomp.py-4.0.5 /opt/zenoss/local
	chown zenoss stomp.py-4.0.5
	su - zenoss
	python stomp.py-4.0.5/setup.py install

This should install stomppy into your Zenoss environment, and now the ActiveMQ ZenPack should have all its dependencies satisfied.

## INSTALLATION - ZenPacks.Eseye.ActiveMQ

To install the ZenPack, the normal ZenPack installation instructions apply.
Simply download the _.egg_ file from this repository and upload it to your Zenoss server.
As the `zenoss` user, run the following command:

	zenpack --install=ZenPacks.Eseye.ActiveMQ-1.4.0-py2.7.egg

This should install the ZenPack.

After installation, remember to place your devices into the `/Server/Linux/ActiveMQ` Device Class and then to set your `zActiveMQUser` and `zActiveMQPassword` in the Device Class so that modelling and polling can be successful.

## What does the ZenPack provide?

This ZenPack will create a __Device Class__ called /Devices/Server/Linux/ActiveMQ and set some default modeler plugins, including but not only `ActiveMQMap`, used to model queues in ActiveMQ servers.

Also will create a __Monitoring Template__ called ActiveMQQueue, which gets automatically assigned to each modelled ActiveMQ Queue (since it has the same name as the ActiveMQQueue python class). This provides graphs that show `consumerCount`, `enqueueCount`, `dequeueCount` and `queueSize`.

It also provides a threshold on `consumerCount` that will raise an Error (escalating to Critical) if the consumer count is 0.

## REMOVING - ZenPacks.Eseye.ActiveMQ

If you remove the `ZenPacks.Eseye.ActiveMQ` ZenPack it will remove the /Devices/Server/Linux/ActiveMQ __Device Class__ ___AND ALL DEVICES UNDER IT!___. Make sure to move the devices under that __Device Class__ somewhere else (maybe _ActiveMQtmp_) before removing the ZenPack!
