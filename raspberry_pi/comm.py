#import pi_gateway
import websocket

ws1 = None

def wsStart():
  global ws1
  ws1 = websocket.WebSocket()
  ws1.start()

def wsSend(msg):
  global ws1
  if ws1 != None:
    #print("SENDE!")
    ws1.send(msg)
