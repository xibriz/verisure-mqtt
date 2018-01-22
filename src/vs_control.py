#!/usr/bin/python
# coding: utf-8

import ConfigParser
import paho.mqtt.publish as publish
import verisure
import codecs
import logging

class VSControl:

    def __init__(self, config_file, logout=True):
        """
        args:
            logout (bool): Log out after each request or stay logged in for
                            faster requests when used in a cron job etc.
        """
        self.logout = logout
        config = ConfigParser.RawConfigParser()
        config.readfp(codecs.open(config_file, 'r', 'utf8'))

        self.mqtt_ip = config.get('MQTT', 'ip')
        self.mqtt_port = config.getint('MQTT', 'port')

        self.armState_sub = config.get('MQTT', 'armState_sub')
        self.armState_status = config.get('MQTT', 'armState_status')

        self.climateValues_status = config.get('MQTT', 'climateValues_status')

        self.doorLock_sub = config.get('MQTT', 'doorLock_sub')
        self.doorLock_status = config.get('MQTT', 'doorLock_status')

        self.doorWindow_status = config.get('MQTT', 'doorWindow_status')

        self.smartPlug_sub = config.get('MQTT', 'smartPlug_sub')
        self.smartPlug_status = config.get('MQTT', 'smartPlug_status')

        self.verisure_username = config.get('Verisure', 'username')
        self.verisure_password = config.get('Verisure', 'password')
        self.verisure_pin = config.get('Verisure', 'pin')

        self.session = None
        self.overview = self._load_status()

    def _load_status(self):
        """
        Load status of all devices
        """
        try:
            self.session = verisure.Session(self.verisure_username, self.verisure_password)
            self.session.login()
            overview = self.session.get_overview()
            if self.logout:
                self.session.logout()

            return overview
        except verisure.session.ResponseError as ex:
            logging.info(ex)
            return None

    def set_arm_state(self, state):
        """
        args:
            state (string): Possible values:
                            ARMED_HOME
                            ARMED_AWAY
                            DISARMED
        """
        try:
            if self.logout:
                self.session = verisure.Session(self.verisure_username, self.verisure_password)
                self.session.login()
            self.session.set_arm_state(self.verisure_pin, state)
            if self.logout:
                self.session.logout()
            return True
        except verisure.session.ResponseError as ex:
            logging.info(ex)
            return False

    def set_door_lock_state(self, area, state):
        """
        args:
            area (string): area/name of lock
            state (string): Possible values:
                            lock
                            unlock
        """
        #Find Door lock id
        deviceLabel = None
        for doorLock in self.overview['doorLockStatusList']:
            if doorLock['area'].replace(' ', '') == area:
                deviceLabel = doorLock['deviceLabel']
                break

        try:
            if self.logout:
                self.session = verisure.Session(self.verisure_username, self.verisure_password)
                self.session.login()
            self.session.set_lock_state(self.verisure_pin, deviceLabel, state)
            if self.logout:
                self.session.logout()
            return True
        except verisure.session.ResponseError as ex:
            logging.info(ex)
            return False

    def set_smart_plug_state(self, area, state):
        """
        args:
            area (string): area/name of lock
            state (boolean): Possible values:
                            True = ON
                            False = OFF
        """
        #Find Smart Plug id
        deviceLabel = None
        for smartPlug in self.overview['smartPlugs']:
            if smartPlug['area'].replace(' ', '') == area:
                deviceLabel = smartPlug['deviceLabel']
                break

        try:
            if self.logout:
                self.session = verisure.Session(self.verisure_username, self.verisure_password)
                self.session.login()
            self.session.set_smartplug_state(deviceLabel, state)
            if self.logout:
                self.session.logout()
            return True
        except verisure.session.ResponseError as ex:
            logging.info(ex)
            return False
