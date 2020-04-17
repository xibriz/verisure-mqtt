#!/usr/bin/python
# coding: utf-8

"""
Publish all other devices except climate values.
Make a cron job that runs every so often:
* * * * * /path/to/verisure-mqtt/venv/bin/python /path/to/verisure-mqtt/publish_devices.py prod.cfg
"""

import sys
config_file = "prod.cfg"
if len(sys.argv) > 1:
    config_file = sys.argv[1]

import os
main_base = os.path.dirname(__file__)
config_file = os.path.join(main_base, "config", config_file)

from src import vs_publish

vs = vs_publish.VSPublish(config_file=config_file, logout=True)

vs.arm_state()
vs.door_lock()
vs.door_window()
vs.smart_plug()
vs.vacation_status()

# vs.door_lock(u'1etGang')
# vs.door_window(u'1etHoveddør')
# vs.smart_plug(u'Telldus')
