# IoT-project
Created during my time at Sato Lab (http://www-sato.cc.u-tokyo.ac.jp) at The University of Tokyo.

This project showcases an Edge Computing application. The basic components are:
* Arduino Uno acting as edge device; equipped with sensors, actuators and a Bluetooth Low Energy module
* Raspberry Pi 3 Model B+ acting as gateway; connected to the Arduino Uno via builtin Bluetooth Low Energy support
* Webserver (vServer located in Germany: 2vCore CPU, 2GB RAM) connected to the Raspberry Pi via Websocket

The idea is to enable a user to view the current sensor readings form anywhere in the world and to activate the actuator(s) with a low latency.
See this video for a demonstration:  

[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/Lw-rmpPToWY/0.jpg)](https://www.youtube.com/watch?v=Lw-rmpPToWY)

## Instructions
To use this example, first set up the hardware as explained and flash your Arduino with the arduino_node.ino code. Next, start the webserver ("ruby server.rb"). Make sure to supply the correct URL in the raspberry_pi/websocket.py file (line 5) and then start the gateway ("python3 pi_gateway.py"). The gateway will connect to the HM-17 of the Arduino and the Webserver automatically. Access the website of your webserver and you should see the control interface. Make sure the Arduino and Raspberry Pi are in range for the bluetooth connection to work.

## Arduino
### Hardware setup
<img src="https://github.com/oli415/IoT-project/blob/master/Arduino_Hardware.jpg" width="500">
This is the BLE module: [DSD TECH HM-17](https://www.amazon.co.jp/dp/B07GNZFDH2/).
To connect it to the Arduino, I used the GPIO pins 8 and 9 for receive (RX) and transmit (TX) respectively. The HM-17 is a 3.3V device, so the 5V from the Arduino should be brought down, as explained in [this guide](http://www.martyncurrey.com/hm-10-bluetooth-4ble-modules/) for the HM-10 (similar module). I used a voltage divider for the connection from the Arduino TX to the HM-10 RX pin (the other way around is fine because the Arduino will see the 3.3V from the HM-10 TX as high).

To showcase a sensor, I used the DHT11 temperature and humidity module that was included in my Arduino package. I used pin 2 on the Arduino for DATA, 5V supply voltage and ground.

As an actuator, I used a simple blue LED connected to pin 13 (connected in series with a 220ohm resistor).

### Code overview
The AltSoftSerial library was used to talk to the HM-17 from the Arduino. It uses pins 8 and 9 as explained in the hardware setup. The code essentially runs an endless loop in which
1. the sensor is read every 5 seconds and the data (including a timestamp) is sent to the HM-17, which sends it over BLE to the gateway.
2. the serial connection to the HM-17 is checked for available data and printed to the ordinary serial connection (*Serial*) to the PC (only necessary for development/debugging); if the data contains a command to turn on or off the blue LED, it is executed there. I used my own protocol to detect commands by denoting the beginning and end of such a message with "#" (e.g. "#LED = ON#").
3. the serial connection to the PC is checked for available data and this is written to the HM-10 serial connection (without line feed and carriage return bytes because that is what the HM-17 specifies). This is not necessary during operation, but I used to talk to the HM-10, for example to read its MAC address with the command "AT+ADDR?". See more details on how to talk to the HM-17 in the [guide](http://www.martyncurrey.com/hm-10-bluetooth-4ble-modules/) already linked above.

## Raspberry Pi
### Code overview
The main file is pi_gateway.py. In it, the library [bluepy](https://ianharvey.github.io/bluepy-doc/) is used to connect to the HM-17 via its MAC address (line 70). A callback function ("Delegate") is set up as specified in the library docs. Now, to talk to the HM-17, a custom characteristic of a service specified by the HM-17 was used. Read more about services and characteristics in [this guide](http://www.martyncurrey.com/hm-10-bluetooth-4ble-modules/). It is important to also subscribe to notifications by writing to the Client Characteristic Configuration descriptor, otherwise no messages from the HM-17 can be received (line 89). In order to facilitate concurrency, the threading library is used to create threads. One thread ("receiveThread") is set up to wait for and handle incoming messages from the HM-17. There is an existing problem with receiving and sending at the same time using bluepy, as discussed [here](https://www.github.com/IanHarvey/bluepy/issues/253). The write function internally awaits an acknowledge. If that acknowledge is picked up by the receiveThread instead, an exception will be thrown (line 51).

The main thread waits for and handles user input, which was useful for testing.
There are two more threads: The first one is the socketThread, which handles the communication with the webserver and will be explained below. The second one is the sendThread which runs and endless loop in which it waits for a signal by the socketThread and sends the available message to the Arduino (HM-17). The waiting and signalling is done using a threading.Condition(), which is created in the comm.py file.

The socketThread is initiated with a routine in comm.py which acts as an interface to the WebSocket class in websocket.py: In it, an instance of the class is created and its start routine is called. In the constructor (defined in websocket.py), a connection to the webserver is established via its URL. I used the websockets library which internally uses asyncio to handle concurrency. The WebSocket start routine waits for messages from the webserver and acts upon them (relays to the Arduino if the "LED = ON" command is received). The sending from Raspberry Pi to the Webserver happens in WebSocket.send(), which is called through an interface function in comm.py by the receiveThread whenever new sensor data is available (py_gateway.py: line 43). The data is sent in JSON format.

## Webserver
### Code overview
I used the Sinatra Ruby framework to create a simple website and server functionality. The webserver code is contained in server.rb: When the homepage is accessed via GET request, the server differentiates between HTTP and WebSocket access. If it is a normal browser access (HTTP), the index page (index.erb) is displayed, which just says that we are waiting for a gateway to connect. If, on the other hand, it is a WebSocket request, which means that the Raspberry Pi Gateway wants to connect, then the first thing that happens is that a flag is set to indicate the connection. When a user now accesses the homepage, they are shown the Arduino Control interface (connected.erb). The connection is opened. The "ws.onmessage" event is used in line 45 to define what should be executed in case a message is received from the Raspberry: The JSON of the message is parsed and checked for validity. In case the check is successful, the data is saved in the class variable @@msg_content.

In the connected.erb view, the user can turn the LED on and off, and display the current sensor readings. These functions are implmented via post methods (form actions). When the actuate button is pressed, the post route '/actuate' in server.rb line 66 is executed. Depending on the selected option (on or off), the corresponding command is sent through the websocket to the Raspberry Pi. When sensor readings are requested, the post route '/display' is executed. If sensor data is available (@@msg_content is set), the view is updated to display the new values.
