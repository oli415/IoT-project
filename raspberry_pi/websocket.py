import asyncio
import websockets
import pi_gateway

URL = 'ws://79cb755.online-server.cloud:4567'

class WebSocket:
  def __init__(self):
    #async with websockets.connect('ws://79cb755.online-server.cloud:4567') as websocket:
    self.ws = None
    self.loop = asyncio.get_event_loop()
    #perform a synchronous connect
    self.loop.run_until_complete(self.wsConnect())
    #await websocket.send("hello from pi")
    #print("From the server:")

  async def wsConnect(self):
    print("attempting connection to {}".format(URL))
    # perform async connect, and store the connected WebSocketClientProtocol
    # object, for later reuse for send & recv
    self.ws = await connect(URL)
    print("connected")

  async def wsRun(self):
    while True:
      response = await self.ws.recv()
      print(response)
      if response == "LED = ON":
        pi_gateway.comm1.sendToArduino(b"#LED = ON#")
      if response == "LED = OFF":
        pi_gateway.comm1.sendToArduino(b"#LED = OFF#")


  async def wsSend(self, msg):
    await self.ws.send(msg)

  def start(self):
    self.new_loop = asyncio.new_event_loop()
    self.new_loop.run_until_complete(self.wsRun())

  def send(self, msg):
    self.loop.run_until_complete(self.wsSend(msg))

