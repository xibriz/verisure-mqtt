#!/usr/bin/python
# coding: utf-8

import configparser
import paho.mqtt.publish as publish
import verisure
import codecs
import logging

class VSPublish:

    def __init__(self, config_file, logout=True):
        """
        args:
            logout (bool): Log out after each request or stay logged in for
                            faster requests when used in a cron job etc.
        """
        self.logout = logout
        config = configparser.SafeConfigParser()
        config.readfp(codecs.open(config_file, 'r', 'utf8'))

        self.mqtt_ip = config.get('MQTT', 'ip')
        self.mqtt_port = config.getint('MQTT', 'port')

        self.armState_pub = config.get('MQTT', 'armState_pub')
        self.vacationState_pub = config.get('MQTT', 'vacationState_pub')
        self.climateValues_pub = config.get('MQTT', 'climateValues_pub')
        self.doorLock_pub = config.get('MQTT', 'doorLock_pub')
        self.doorWindow_pub = config.get('MQTT', 'doorWindow_pub')
        self.smartPlug_pub = config.get('MQTT', 'smartPlug_pub')

        self.verisure_username = config.get('Verisure', 'username')
        self.verisure_password = config.get('Verisure', 'password')

        self.session = None
        self.overview = None
        self.vacation = None
        self._load_status()

    def _load_status(self):
        """
        Load status of all devices
        """
        try:
            self.session = verisure.Session(self.verisure_username, self.verisure_password)
            self.session.login()
            self.overview = self.session.get_overview()
            self.vacation = self.session.get_vacation_mode()
            if (self.logout):
                self.session.logout()
            #print self.overview
        except verisure.session.ResponseError as ex:
            logging.info(ex)
            return None

    def arm_state(self, loadStatus = False):
        """
        Publish arm state
        """
        if loadStatus:
            self._load_status()
        if self.overview is None:
            return False
        topic = self.armState_pub

        try:
            publish.single(u'{}/statusType'.format(topic), self.overview['armState']['statusType'], hostname=self.mqtt_ip, port=self.mqtt_port)
        except KeyError as ex:
            logging.info(ex)
            pass
        try:
            publish.single(u'{}/changedVia'.format(topic), self.overview['armState']['changedVia'], hostname=self.mqtt_ip, port=self.mqtt_port)
        except KeyError as ex:
            logging.info(ex)
            pass

        return True

    def climate_values(self, deviceAreaPublish = None, loadStatus = False):
        """
        Publish climate values
        args:
            deviceAreaPublish (string): If given, only publish this deviceArea
        """
        if loadStatus:
            self._load_status()
        if self.overview is None:
            return False
        elif not self.overview['climateValues']:
            return None

        for climate in self.overview['climateValues']:
            deviceArea = climate['deviceArea'].replace(' ', '')
            if deviceAreaPublish is not None and deviceAreaPublish != deviceArea:
                 continue
            topic = self.climateValues_pub.format(deviceType=climate['deviceType'], deviceArea=deviceArea)
            try:
                publish.single(u'{}/temperature'.format(topic), climate['temperature'], hostname=self.mqtt_ip, port=self.mqtt_port)
            except KeyError as ex:
                logging.info(ex)
                pass
            try:
                publish.single(u'{}/humidity'.format(topic), climate['humidity'], hostname=self.mqtt_ip, port=self.mqtt_port)
            except KeyError as ex:
                logging.info(ex)
                pass
            if deviceAreaPublish is not None and deviceAreaPublish == deviceArea:
                 break

        return True

    def door_lock(self, areaPublish = None, loadStatus = False):
        """
        Publish door lock status
        args:
            areaPublish (string): If given, only publish this area
        """
        if loadStatus:
            self._load_status()
        if self.overview is None:
            return False
        elif not self.overview['doorLockStatusList']:
            return None

        for doorLock in self.overview['doorLockStatusList']:
            area = doorLock['area'].replace(' ', '')
            if areaPublish is not None and areaPublish != area:
                continue
            topic = self.doorLock_pub.format(area=area)
            try:
                publish.single(u'{}/currentLockState'.format(topic), doorLock['currentLockState'], hostname=self.mqtt_ip, port=self.mqtt_port)
            except KeyError as ex:
                logging.info(ex)
                pass
            if areaPublish is not None and areaPublish == area:
                break

        return True


    def door_window(self, areaPublish = None, loadStatus = False):
        """
        Publish door window status
        args:
            areaPublish (string): If given, only publish this area
        """
        if loadStatus:
            self._load_status()
        if self.overview is None:
            return False
        elif not self.overview['doorWindow']['doorWindowDevice']:
            return None

        for doorWindow in self.overview['doorWindow']['doorWindowDevice']:
            area = doorWindow['area'].replace(' ', '')
            if areaPublish is not None and areaPublish != area:
                continue
            topic = self.doorWindow_pub.format(area=area)
            try:
                publish.single(u'{}/state'.format(topic), doorWindow['state'], hostname=self.mqtt_ip, port=self.mqtt_port)
            except KeyError as ex:
                logging.info(ex)
                pass
            if areaPublish is not None and areaPublish == area:
                break

        return True

    def smart_plug(self, areaPublish = None, loadStatus = False):
        """
        Publish smart plug status
        args:
            areaPublish (string): If given, only publish this area
        """
        if loadStatus:
            self._load_status()
        if self.overview is None:
            return False
        elif not self.overview['smartPlugs']:
            return None

        for smartPlug in self.overview['smartPlugs']:
            area = smartPlug['area'].replace(' ', '')
            if areaPublish is not None and areaPublish != area:
                continue
            topic = self.smartPlug_pub.format(area=area)
            try:
                publish.single(u'{}/currentState'.format(topic), smartPlug['currentState'], hostname=self.mqtt_ip, port=self.mqtt_port)
            except KeyError as ex:
                logging.info(ex)
                pass
            if areaPublish is not None and areaPublish == area:
                break

        return True

    def vacation_status(self, loadStatus = False):
        """
        Publish vacation tatus
        """
        if loadStatus:
            self._load_status()
        if self.vacation is None:
            return False
        elif 'cid' not in self.vacation:
            return None
        topic = self.vacationState_pub

        for key, value in self.vacation.items():
            try:
                publish.single(u'{}/{}'.format(topic, key), value, hostname=self.mqtt_ip, port=self.mqtt_port)
            except KeyError as ex:
                logging.info(ex)
                pass

