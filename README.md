# verisure-mqtt
Publish verisure devices to MQTT

Based on https://github.com/persandstrom/python-verisure

## Installation
$ git clone https://github.com/xibriz/verisure-mqtt.git
$ cd verisure-mqtt
$ python3 -m venv venv
$ source venv/bin/activate
$ pip3 install pip --upgrade
$ pip3 install -r requirements.txt

## Configuration

Copy `config/default.cfg` to `config/prod.cfg` and fill in all the FIXME values

## Publish

Device and climate values can be published by running the files `publish_climate.py` and `publish_devices.py`
There are instructions in each file on how to set up a cron job

## Subscribe

Change the `WorkingDirectory` in `verisure-mqtt.service`

Copy the .service-file to the system folder an enable the service-file

```
Ubuntu:
$ sudo cp verisure-mqtt.service /etc/systemd/service/
$ sudo systemctl enable verisure-mqtt.service
$ sudo systemctl start verisure-mqtt.service

CentOS:
$ sudo cp verisure-mqtt.service /etc/systemd/system/
$ sudo systemctl enable verisure-mqtt.service
$ sudo systemctl start verisure-mqtt.service

```

## Examples

The MQTT output from the publish scripts will look something like this:

```
verisure/armState/statusType ARMED_AWAY
verisure/armState/changedVia CODE
verisure/doorLock/YourLock/currentLockState LOCKED
verisure/doorWindow/YourDoorWindowSensor/state CLOSE
verisure/smartPlug/YourSmartPlug/currentState ON
verisure/climateValues/SMOKE2/YourSmokeDetector/temperature 24.8
verisure/climateValues/SMOKE2/YourSmokeDetector/humidity 25.0
verisure/climateValues/WATER1/YourWaterDetector/temperature 20.0
verisure/climateValues/SIREN1/YourKitchenSiren/temperature 21.0
```

The following MQTT topics are available to control the system:

Alarm functions
```
$ mosquitto_pub -t 'verisure/armState/set' -m 'DISARMED'
$ mosquitto_pub -t 'verisure/armState/set' -m 'ARMED_HOME'
$ mosquitto_pub -t 'verisure/armState/set' -m 'ARMED_AWAY'
$ mosquitto_pub -t 'verisure/armState/status' -m ''
```

SmartPlug functions
```
$ mosquitto_pub -t 'verisure/smartPlug/YourSmartPlug/set' -m 'false'
$ mosquitto_pub -t 'verisure/smartPlug/YourSmartPlug/set' -m 'true'
$ mosquitto_pub -t 'verisure/smartPlug/YourSmartPlug/status' -m ''
```

DoorLock functions
```
$ mosquitto_pub -t 'verisure/doorLock/YourLock/set' -m 'unlock'
$ mosquitto_pub -t 'verisure/doorLock/YourLock/set' -m 'lock'
$ mosquitto_pub -t 'verisure/doorLock/YourLock/status' -m ''
```

DoorWindow functions
```
mosquitto_pub -t 'verisure/doorWindow/YourDoorWindowSensor/status' -m ''
```

Climate functions
```
mosquitto_pub -t 'verisure/climateValues/SMOKE2/YourSmokeDetector/status' -m ''
mosquitto_pub -t 'verisure/climateValues/WATER1/YourWaterDetector/status' -m ''
mosquitto_pub -t 'verisure/climateValues/SIREN1/YourKitchenSiren/status' -m ''
```
