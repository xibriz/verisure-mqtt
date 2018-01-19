#!/usr/bin/python
# coding: utf-8

import os
main_base = os.path.dirname(__file__)
config_file = os.path.join(main_base, "config", "prod.cfg")

import paho.mqtt.client as mqtt
import re
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

# control.set_arm_state("DISARMED")
# control.set_arm_state("ARMED_HOME")
# control.set_arm_state("ARMED_AWAY")

# print control.set_door_lock_state("1etGang", "unlock")
# print control.set_door_lock_state("1etGang", "lock")

# print control.set_smart_plug_state("Telldus", False)
# print control.set_smart_plug_state("Telldus", True)

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
        vsp.arm_state()

    m = rg_armState_status.search(msg.topic)
    if m:
        # name = m.group(1)
        vsp.arm_state()

    m = rg_climateValues_status.search(msg.topic)
    if m:
        vsp.climate_values(m.group(2))

    m = rg_doorLock_set.search(msg.topic)
    if m:
        area = m.group(1)
        vsc.set_door_lock_state(area, msg.payload)
        vsp.door_lock(area)

    m = rg_doorLock_status.search(msg.topic)
    if m:
        vsp.door_lock(m.group(1))

    m = rg_doorWindow_status.search(msg.topic)
    if m:
        vsp.door_window(m.group(1))

    m = rg_smartPlug_set.search(msg.topic)
    if m:
        area = m.group(1)
        vsc.set_smart_plug_state(area, msg.payload)
        vsp.smart_plug(area)

    m = rg_smartPlug_status.search(msg.topic)
    if m:
        vsp.smart_plug(m.group(1))



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
