import bluepy.btle as btle
import time
import binascii

class ReceiveDelegate(btle.DefaultDelegate):
  def __init__(self):
    btle.DefaultDelegate.__init__(self)

  def handleNotification(self, cHandle, data):
    print(data.decode("utf-8"))

print "Connecting..."
dev = btle.Peripheral("F0:F8:F2:C3:6A:04")
dev.withDelegate(ReceiveDelegate())

#print "Services..."
#for svc in dev.services:
#  print str(svc)

bidir_uuid = btle.UUID("0000ffe0-0000-1000-8000-00805f9b34fb")
bidir_service = dev.getServiceByUUID(bidir_uuid)
#print "Characteristics for ffe0 service..."
#for ch in bidir_service.getCharacteristics():
#  print str(ch)

bidir_char = bidir_service.getCharacteristics()[0]

# write 1 to the Client Characteristic Configuration descriptor (one handle after the custom characteristic) -> enable notifications
cccd = bidir_char.valHandle + 1
dev.writeCharacteristic(cccd, b"\x01\x00")


#bidir_char.write(bytes("Hello world\n"))

#val = bidir_char.read()
#print "ffe1 characteristic value", binascii.b2a_hex(val)



while True:
  if dev.waitForNotifications(1):
    continue


dev.disconnect()
print "Disconnected!"
