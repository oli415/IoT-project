import threading
import sys
from arduino_comm import ArduinoComm
from websocket import wsStart

# start thread for receiving from Arduino
comm1 = ArduinoComm()
try:
  receiveThread = threading.Thread(target = comm1.waitForNotifications)
  receiveThread.daemon = True # the entire python program exits when only daemon threads are left
  receiveThread.start()
except:
  print("Error: unable to start Arduino receive thread")

# start thread for communicating with webserver
try:
  socketThread = threading.Thread(target = wsStart)
  socketThread.daemon = True
  socketThread.start()
except:
  print("Error: unable to start websocket comm thread")

# start program (user input) loop
while 1:
  sys.stdout.write('>')
  userInput = input()
  #print "You entered %s" % userInput
  if userInput == "exit":
    comm1.arduinoDisconnect()
    break
  elif userInput == "led on":
    comm1.sendToArduino(b"#LED = ON#")
  elif userInput == "led off":
    comm1.sendToArduino(b"#LED = OFF#")
  else:
    print("Command unknown!")

print("Goodbye!")
