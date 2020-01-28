import bluepy.btle as btle
import binascii
import os
import json

# class used for handling incoming notifications from the Arduino
class ReceiveDelegate(btle.DefaultDelegate):
  def __init__(self):
    btle.DefaultDelegate.__init__(self)

  def handleNotification(self, cHandle, data):
    import pi_gateway
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
      #print(msg_json)
      pi_gateway.ws1.send(msg_json)

class ArduinoComm:
  def __init__(self):
    # SETUP
    print("Connecting...")
    self.dev = btle.Peripheral("F0:F8:F2:C3:6A:04")
    self.dev.withDelegate(ReceiveDelegate())

    #print("Services...")
    #for svc in self.dev.services:
    #  print(str(svc))

    bidir_uuid = btle.UUID("0000ffe0-0000-1000-8000-00805f9b34fb") # the custom service
    bidir_service = self.dev.getServiceByUUID(bidir_uuid)
    #print("Characteristics for ffe0 service...")
    #for ch in self.bidir_service.getCharacteristics():
    #  print(str(ch))

    self.bidir_char = bidir_service.getCharacteristics()[0] # the custom characteristic (ffe1)
    #val = self.bidir_char.read()
    #print("ffe1 characteristic value", binascii.b2a_hex(val))

    # write 1 to the Client Characteristic Configuration descriptor (one handle after the custom$
    cccd = self.bidir_char.valHandle + 1
    #val = self.dev.readCharacteristic(cccd)
    #print("CCCD value before = ", binascii.b2a_hex(val))
    self.dev.writeCharacteristic(cccd, b"\x01\x00")
    #val = self.dev.readCharacteristic(cccd)
    #print("CCCD value after = ", binascii.b2a_hex(val))
    # SETUP DONE


  # receive handler function
  def waitForNotifications(self):
    while True:
      try:
        if self.dev.waitForNotifications(1.0): #handleNotification() will be called when a message is received
         pass
      except btle.BTLEException as e:
        if str(e) == "Unexpected response (wr)":  # https://www.github.com/IanHarvey/bluepy/is$
          print("CAUGHT!")
          os._exit(0)
        else:
          print("BTLEException: " + str(e))
      except btle.BTLEDisconnectError:
        return

  def sendToArduino(self, msg):
    try:
      self.bidir_char.write(msg)
    except btle.BTLEDisconnectError:
      self.arduinoDisconnect()

  def arduinoDisconnect(self):
    self.dev.disconnect()
    print("Disconnected!")
