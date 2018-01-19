#!/usr/bin/python
# coding: utf-8

"""
Publish all other devices except climate values.
Make a cron job that runs every so often:
* * * * * /usr/bin/python /path/to/publish_devices.py
"""

import os
main_base = os.path.dirname(__file__)
config_file = os.path.join(main_base, "config", "prod.cfg")

from src import vs_publish

vs = vs_publish.VSPublish(config_file=config_file, logout=False)
vs.arm_state()
vs.door_lock()
vs.door_window()
vs.smart_plug()

# vs.door_lock(u'1etGang')
# vs.door_window(u'1etHoveddør')
# vs.smart_plug(u'Telldus')
