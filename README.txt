# README

## DEPENDENCIES

`stomppy` (python library for STOMP communication with ActiveMQ)<br/>
`pythonssl` (stomppy dep. - included in Zenoss environment)

## INSTALLATION - stomppy

To install, there are a few steps. Because the Python environment for Zenoss __is not__ the same as for the system, you cannot install `stomppy` with an _.RPM_ package, as this would install it for the system environment. You must install `stomppy` manually as the Zenoss user.

To download the _.RPM_ file, go [here](https://code.google.com/p/stomppy/downloads/list) and download the __version 3.1.3__ _.tar.gz_. You will then need to upload it to your zenoss server.

Un-tar the file by running `tar -zxvf stomppy-3.1.3.tar.gz` and then move the resulting file to a temporary folder in the zenoss home folder. This could be a sequence of instructions to follow:

	sudo su
	tar -zxvf stomppy-3.1.3.tar.gz
	mkdir /opt/zenoss/local
	mv stomppy-3.1.3 /opt/zenoss/local
	chown zenoss stomppy-3.1.3
	su - zenoss
	python stomppy-3.1.3/setup.py install

This should install stomppy into your Zenoss environment, and now the ActiveMQ ZenPack should have all its dependencies satisfied.

Another way to install `stomppy` is via the `easy_install-2.7` script that comes with Zenoss. The instructions to do this are simple:

As the `zenoss` user, run the `easy_install-2.7` script with a `.tar.gz` python package as a command-line argument. The script will download the package and run `setup.py` for you.

Lets say the download link for our `.tar.gz` file is https://code.google.com/p/stomppy/download (which it isn't, but just for the sake of example). These are the commands we would have to run.

	sudo su
	su - zenoss
	cd /opt/zenoss/bin
	easy_install-2.7 https://code.google.com/p/stomppy/download

And that should install the package for you as the `zenoss` user.

## INSTALLATION - ZenPacks.Eseye.ActiveMQ

To install the ZenPack, the normal ZenPack installation instructions apply.
Simply download the _.egg_ file from [here](http://some_url.com/activemq_zenpack) and upload it to your Zenoss server.
As the `zenoss` user, run the following command:

	zenpack --install=ZenPacks.Eseye.ActiveMQ-1.4.0-py2.7.egg

This should install the ZenPack.

## What does the ZenPack provide?

This ZenPack will create a __Device Class__ called /Devices/Server/Linux/ActiveMQ and set some default modeler plugins, including but not only `ActiveMQMap`, used to model queues in ActiveMQ servers.

Also will create a __Monitoring Template__ called ActiveMQQueue, which gets automatically assigned to each modelled ActiveMQ Queue (since it has the same name as the ActiveMQQueue python class). This provides graphs that show `consumerCount`, `enqueueCount` and `queueSize`.

It also provides a threshold on `consumerCount` that will raise an Error (escalating to Critical) if the consumer count is 0.

## REMOVING - ZenPacks.Eseye.ActiveMQ

If you remove the `ZenPacks.Eseye.ActiveMQ` ZenPack it will remove the /Devices/Server/Linux/ActiveMQ __Device Class__ ___AND ALL DEVICES UNDER IT!___. Make sure to move the devices under that __Device Class__ somewhere else (maybe _ActiveMQtmp_) before removing the ZenPack!