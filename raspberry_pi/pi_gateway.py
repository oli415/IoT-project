import threading
import sys
import arduino_comm
import websocket

arduino_comm.init()
# start thread for receiving from Arduino
try:
  receiveThread = threading.Thread(target = arduino_comm.start)
  receiveThread.daemon = True # the entire python program exits when only daemon threads are left
  receiveThread.start()
except:
  print("Error: unable to start Arduino receive thread")

# start thread for communicating with webserver
#ws1 = websocket.WebSocket()
#try:
 # socketThread = threading.Thread(target = ws1.start)
  #socketThread.daemon = True
  #socketThread.start()
#except:
 # print("Error: unable to start websocket comm thread")

# start program (user input) loop
while 1:
  sys.stdout.write('>')
  userInput = input()
  #print "You entered %s" % userInput
  if userInput == "exit":
    arduino_comm.arduinoDisconnect()
    break
  elif userInput == "led on":
    arduino_comm.sendToArduino(b"#LED = ON#")
  elif userInput == "led off":
    arduino_comm.sendToArduino(b"#LED = OFF#")
  else:
    print("Command unknown!")

print("Goodbye!")
