# Monaden internet of things
This repo contains the code controlling and maintaining the smart devices which can be found in Monaden, our home. As of writing this, there are about 13 IKEA TRADFRI color bulbs, one TRADFRI remote controller, and a Chromecast. Besides this, there also is a local hosted [web application](http://megaserver/). The remote and web application can be used to control the lights and Chromecast.

## The server
To work on this project you need access to the server running the application. Do so by speaking to the person in charge, or [the board](styrelsen@dvet.se). They will grant you ssh access. To restart the application use ```sudo systemctl restart iot```, and ```sudo journalctl -u iot``` to view application logs. 

## Zigbee 3.0 USB Dongle plus
These lights and controller is controlled with a Zigbee 3.0 USB Dongle plus over zigbee radio protocol. 

## Zigbee2MQTT
The zigbee communication through the dongle is simplified to MQTT through Zigbee2MQTT. For more details one could look through the [Zigbee2MQTT dir](zigbee2mtqq). To begin with, the docker container running Zigbee2MQTT can be started with the [compose file](zigbee2mtqq/docker-compose.yml)(use ```docker-compose up``` to start, ```docker-compose up``` to shut down). This will start, the MQTT broker zigbee translator, and mqtt client, but also a web interface to interact with it. With the current setup, it can be accessed at port [2512](http://localhost:2512) when activated. The easiest way to connect devices in pairing mode is to click the "permit all" button use this UI under the "TouchLink" tab and then click the scan button. 


## IKEA TRADFRI color bulbs
The bulbs are controlled with MQTT via Zigbee2MQTT, one or several at a time. They can change intensity, color, and warmth. They can be butt into pairing mode by switching them on and on 6 times, https://www.youtube.com/watch?v=npxOrPxVfe0. 

## RADFRI remote controller
This remote similarly can be heard through MQTT via Zigbee2MQTT. It has 5 buttons to press, 4 of which can be held. Each action is distinct. The remote can be put in pairing mode by holding it close to the coordinator and pressing the inside button, next to the CR2032 battery, 4 times in 5s. **You can control the light and Chromecast with this remote**. The colors are currently limited to red, blue, and purple.

## Web application
The web application has a simple interface and a Flask backend, which is admissible. **Through this UI, you can also control the lights and Chromecast**. However, color of the lights can be freely picked while only volume control has been implemented for the Chromecast. 

## Server application
The [server application](frontend/app.py) runs the flask web application, zigbee2mqtt and its devices, and the Chromecast control in separate processes. By design, if one is not working the others can still function. 

## Device scripting
To create a new script use the lights and remote is rather simple by defining a method which takes a MonadenKit as argument, as show in [main.py](main.py). The MonadenKit data class contains all the devices as well as all lights as a group. By addressing the lights as a group, they can be controlled simultaneously in an instant. 