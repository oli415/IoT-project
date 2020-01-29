import asyncio
import websockets
import comm

URL = 'ws://79cb755.online-server.cloud:4567'

class WebSocket:
  def __init__(self):
    #async with websockets.connect('ws://79cb755.online-server.cloud:4567') as websocket:
    self.ws = None
    self.loop = asyncio.new_event_loop()
    #perform a synchronous connect
    self.loop.run_until_complete(self.wsConnect())

  async def wsConnect(self):
    print("attempting connection to {}".format(URL))
    # perform async connect, and store the connected WebSocketClientProtocol object, for later reuse for send & recv
    self.ws = await websockets.connect(URL)
    print("connected")

  async def wsRun(self):
    while True:
      response = await self.ws.recv()
      print(response)
      if response == "LED = ON":
        comm.sendToArduino(b"#LED = ON#")
      if response == "LED = OFF":
        comm.sendToArduino(b"#LED = OFF#")

  async def wsSend(self, msg):
    await self.ws.send(msg)

  def start(self):
    self.loop.run_until_complete(self.wsRun())

  def send(self, msg):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(self.wsSend(msg))
    #asyncio.ensure_future(self.wsSend(msg))
    #self.loop.run_until_complete(self.wsSend(msg))
    #self.loop.run(self.wsSend(msg))
    #task_obj = self.loop.create_task(self.wsSend(msg))
    #self.loop.run_until_complete(task_obj)
