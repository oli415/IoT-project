import bluepy.btle as btle
import binascii
import threading
import sys
import os
import json
#import websocket
import comm

def sendToArduino(msg):
  try:
    bidir_char.write(msg)
  except btle.BTLEDisconnectError:
    arduinoDisconnect()

def arduinoDisconnect():
  dev.disconnect()
  print("Disconnected!")

# class used for handlng incoming notifications from the Arduino
class ReceiveDelegate(btle.DefaultDelegate):
  def __init__(self):
    btle.DefaultDelegate.__init__(self)

  def handleNotification(self, cHandle, data):
    #print("")
    #print("ARDUINO: " + data.decode("utf-8"))
    msg = data.decode("utf-8")
    msg_list = msg.split("=")
    #print(msg_list)
    if msg_list[0] == "T" and msg_list[1][-1] == "H" and msg_list[2][-1] == "t" and msg_list[-1][-1] == "s":
      msg_obj = {}
      msg_obj['T'] = msg_list[1].split(",")[0]
      msg_obj['H'] = msg_list[2].split(",")[0]
      msg_obj['t'] = msg_list[3]
      msg_json = json.dumps(msg_obj)
      print(msg_json)
      comm.wsSend(msg_json)

# Thread function
def waitForNotifications():
  while True:
    try:
      if dev.waitForNotifications(1.0):
        pass
    except btle.BTLEException as e:
      if str(e) == "Unexpected response (wr)":  # https://www.github.com/IanHarvey/bluepy/issues/253
        print("CAUGHT!")
        #dev.disconnect()
        #print "Disconnected!"
        os._exit(0)
    except btle.BTLEDisconnectError:
      return

# start thread for communicating with webserver
try:
  socketThread = threading.Thread(target = comm.wsStart)
  socketThread.daemon = True
  socketThread.start()
except:
  print("Error: unable to start websocket comm thread")

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

# write 1 to the Client Characteristic Configuration descriptor (one handle after the custom characteristic) -> enable$
cccd = bidir_char.valHandle + 1
dev.writeCharacteristic(cccd, b"\x01\x00")
# SETUP DONE

try:
  receiveThread = threading.Thread(target = waitForNotifications)
  receiveThread.daemon = True
  receiveThread.start()
except:
  print("Error: unable to start thread")

# start program (user input) loop
while 1:
  sys.stdout.write('>')
  userInput = input()
  #print "You entered %s" % userInput
  try:
    if userInput == "exit":
      dev.disconnect()
      print("Disconnected BTLE!")
      break
    elif userInput == "led on":
      bidir_char.write(b"#LED = ON#")
    elif userInput == "led off":
      bidir_char.write(b"#LED = OFF#")
    else:
      print("Command unknown!")
  except btle.BTLEDisconnectError:
    dev.disconnect()
    print("Disconnected BTLE!")

print("Goodbye!")
