import bluepy.btle as btle
import time
import binascii
import threading
import sys
import os
import asyncio
from websocket import wsStart

# class used for handlng incoming notifications from the Arduino
class ReceiveDelegate(btle.DefaultDelegate):
  def __init__(self):
    btle.DefaultDelegate.__init__(self)

  def handleNotification(self, cHandle, data):
    print("")
    #print("ARDUINO: " + data.decode("utf-8"))

# Thread function
threadStop = 0
def waitForNotifications():
  while True:
    try:
      if dev.waitForNotifications(1.0):
        pass
      if threadStop == 1:
        return
    except btle.BTLEException as e:
      if str(e) == "Unexpected response (wr)":  # https://www.github.com/IanHarvey/bluepy/issues/253
        print("CAUGHT!")
        #dev.disconnect()
        #print "Disconnected!"
        os._exit(0)
    except btle.BTLEDisconnectError:
      return

# SETUP
print("Connecting...")
dev = btle.Peripheral("F0:F8:F2:C3:6A:04")
dev.withDelegate(ReceiveDelegate())

#print("Services...")
#for svc in dev.services:
#  print(str(svc))

bidir_uuid = btle.UUID("0000ffe0-0000-1000-8000-00805f9b34fb") # the custom service
bidir_service = dev.getServiceByUUID(bidir_uuid)
#print("Characteristics for ffe0 service...")
#for ch in bidir_service.getCharacteristics():
#  print(str(ch))

bidir_char = bidir_service.getCharacteristics()[0] # the custom characteristic (ffe1)
#val = bidir_char.read()
#print("ffe1 characteristic value", binascii.b2a_hex(val))

# write 1 to the Client Characteristic Configuration descriptor (one handle after the custom characteristic) -> enable notifications
cccd = bidir_char.valHandle + 1
dev.writeCharacteristic(cccd, b"\x01\x00")
# SETUP DONE

# start thread for receiving from Arduino
try:
  receiveThread = threading.Thread(target = waitForNotifications)
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

num = 0
while 1:
  sys.stdout.write('>')
  userInput = input()
  #print "You entered %s" % userInput
  try:
    if userInput == "exit":
      threadStop = 1
      dev.disconnect()
      print("Disconnected!")
      break
    elif userInput == "led on":
      bidir_char.write(b"#LED = ON#")
    elif userInput == "led off":
      bidir_char.write(b"#LED = OFF#")
    else:
      print("Command unknown!")
  except btle.BTLEDisconnectError:
    dev.disconnect()
    print("Disconnected!")
