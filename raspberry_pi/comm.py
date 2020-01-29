#import pi_gateway
import websocket
import threading

ws1 = None

new_msg = None
condition = threading.Condition()

def wsStart():
  global ws1
  ws1 = websocket.WebSocket()
  ws1.start()

def wsSend(msg):
  global ws1
  if ws1 != None:
    #print("SENDE!")
    ws1.send(msg)

def getNewMsg():
  global new_msg
  return new_msg

def getCondition():
  global condition
  return condition

def sendToArduino(msg):
  global new_msg
  global condition
  condition.acquire()
  new_msg = msg
  condition.notify()
  condition.release()
