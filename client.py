#!/usr/bin/python
# coding: utf-8

import os
main_base = os.path.dirname(__file__)
config_file = os.path.join(main_base, "config", "prod.cfg")

import logging
import requests

try:
	import http.client as http_client
except ImportError:
	import httplib as http_client
http_client.HTTPConnection.debuglevel = 1

log_file = os.path.join(main_base, "log", "debug.txt")
logging.basicConfig(filename=log_file, level=logging.DEBUG)
logging.getLogger().setLevel(logging.DEBUG)


requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True


import paho.mqtt.client as mqtt
import re
import threading
from src import vs_control
from src import vs_publish

vsp = vs_publish.VSPublish(config_file=config_file, logout=False)
vsc = vs_control.VSControl(config_file=config_file, logout=False)

base = u'^{}$'

rg_armState_set = re.compile(base.format(vsc.armState_sub.format(name='(.*?)').replace('/','\\/')), re.U)
rg_armState_status = re.compile(base.format(vsc.armState_status.format(name='(.*?)').replace('/','\\/')), re.U)

rg_climateValues_status = re.compile(base.format(vsc.climateValues_status.format(deviceType='(.*?)', deviceArea='(.*?)').replace('/','\\/')), re.U)

rg_doorLock_set = re.compile(base.format(vsc.doorLock_sub.format(area='(.*?)').replace('/','\\/')), re.U)
rg_doorLock_status = re.compile(base.format(vsc.doorLock_status.format(area='(.*?)').replace('/','\\/')), re.U)

rg_doorWindow_status = re.compile(base.format(vsc.doorWindow_status.format(area='(.*?)').replace('/','\\/')), re.U)

rg_smartPlug_set = re.compile(base.format(vsc.smartPlug_sub.format(area='(.*?)').replace('/','\\/')), re.U)
rg_smartPlug_status = re.compile(base.format(vsc.smartPlug_status.format(area='(.*?)').replace('/','\\/')), re.U)

status_delay = 10.0

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
	#print("Connected with result code "+str(rc))

	# Subscribing in on_connect() means that if we lose the connection and
	# reconnect then subscriptions will be renewed.
	client.subscribe("verisure/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
	#print(msg.topic+" "+str(msg.payload))
	m = rg_armState_set.search(msg.topic)
	if m:
		# name = m.group(1)
		vsc.set_arm_state(msg.payload)

		arm = threading.Timer(status_delay, vsp.arm_state, [True])
		arm.daemon = True
		arm.start()

	m = rg_armState_status.search(msg.topic)
	if m:
		# name = m.group(1)
		vsp.arm_state(True)

	m = rg_climateValues_status.search(msg.topic)
	if m:
		vsp.climate_values(m.group(2), True)

	m = rg_doorLock_set.search(msg.topic)
	if m:
		area = m.group(1)
		vsc.set_door_lock_state(area, msg.payload)

		lock = threading.Timer(status_delay, vsp.door_lock, [area, True])
		lock.daemon = True
		lock.start()

	m = rg_doorLock_status.search(msg.topic)
	if m:
		vsp.door_lock(m.group(1), True)

	m = rg_doorWindow_status.search(msg.topic)
	if m:
		vsp.door_window(m.group(1), True)

	m = rg_smartPlug_set.search(msg.topic)
	if m:
		area = m.group(1)
		vsc.set_smart_plug_state(area, msg.payload)

		lock = threading.Timer(status_delay, vsp.smart_plug, [area, True])
		lock.daemon = True
		lock.start()

	m = rg_smartPlug_status.search(msg.topic)
	if m:
		vsp.smart_plug(m.group(1), True)



client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(vsp.mqtt_ip, vsp.mqtt_port, 60)

# Publish the status of all devices
vsp.arm_state()
vsp.door_lock()
vsp.door_window()
vsp.smart_plug()
vsp.climate_values()

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
