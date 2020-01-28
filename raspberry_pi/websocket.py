import asyncio
import websockets

async def wsRun():
  async with websockets.connect('ws://79cb755.online-server.cloud:4567') as websocket:
    #await websocket.send("hello from pi")
    #print("From the server:")

    while True:
      response = await websocket.recv()
      print(response)
      #if response == "LED = ON":
      

def wsStart():
  loop = asyncio.new_event_loop()
  loop.run_until_complete(wsRun())

