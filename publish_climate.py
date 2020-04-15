#!/usr/bin/python
# coding: utf-8

"""
Climate sensors are only updated once every 6 hour so there is no point publishing these too often
Make a cron job that runs every 6th hour:
0 */6 * * * /usr/bin/python /path/to/publish_climate.py prod.cfg
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
vs.climate_values()
# vs.climate_values(u'2etGarasje')
