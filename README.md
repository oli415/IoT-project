# IoT-project
Created during my time at Sato Lab (http://www-sato.cc.u-tokyo.ac.jp/at) at The University of Tokyo.

This project showcases an Edge Computing application. The basic components are:
* Arduino Uno acting as edge device; equipped with sensors, actuators and a Bluetooth Low Enerey module
* Raspberry Pi 3 Model B+ acting as gateway; connected to the Arduino Uno via builtin Bluetooth Low Energy support
* Webserver (vServer located in Germany: 2vCore CPU, 2GB RAM) connected to the Raspberry Pi via Websocket

The idea is to enable a user to view the current sensor readings form anywhere in the world and to activate the actuator(s) with a low latency.
See this video for a demonstration:
# INSER VIDEO HERE!

## Arduino
### Hardware setup
(image url "Logo Title Text 1")
This is the BLE module: [DSD TECH HM-17](https://www.amazon.co.jp/dp/B07GNZFDH2/).
To connect it to the Arduino, I used the GPIO pins 8 and 9 for receive (RX) and transmit (TX) respectively. The HM-17 is a 3.3V device, so the 5V from the Arduino should be brought down, as explained in [this guide](http://www.martyncurrey.com/hm-10-bluetooth-4ble-modules/) for the HM-10 (similar module). I used a voltage divider for the connection from the Arduino TX to the HM-10 RX pin (the other way around is fine because the Arduino will see the 3.3V from the HM-10 TX as high).

To showcase a sensor, I used the DHT11 temperature and humidity module that was included in my Arduino package. I used pin 2 on the Arduino for DATA, 5V supply voltage and ground.

As an actuator, I used a simple blue LED connected to pin 13 (connected in series with a 220ohm resistor).

### Code overview

The AltSoftSerial library was used to talk to the HM-10 from the Arduino. It uses pins 8 and 9 as explained in the hardware setup. The code essentially runs an endless loop in which
1. the sensor is read every 5 seconds and the data (including a timestamp) is sent to the HM-10, which sends it over BLE to the gateway.
2. the serial connection to the HM-10 is checked for available data and printed to the ordinary serial connection (*Serial*) to the PC (only necessary for development/debugging); if the data contains a command to turn on or off the blue LED, it is executed there.
3. the serial connection to the PC is checked for available data and this is written to the HM-10 serial connection (without line feed and carriage return bytes because that is what the HM-10 specifies). This is not necessary during operation, but I used to talk to the HM-10, for example to read its MAC address with the command "AT+ADDR?". See more details on how to talk to the HM-10 in the [guide](http://www.martyncurrey.com/hm-10-bluetooth-4ble-modules/) already linked above.
