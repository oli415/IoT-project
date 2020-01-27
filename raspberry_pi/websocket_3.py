import asyncio
import websockets

async def test():

  async with websockets.connect('ws://79cb755.online-server.cloud:4567') as websocket:

    await websocket.send("hello from pi")

    print("From the server:")

    while True:
      response = await websocket.recv()
      print(response)

asyncio.get_event_loop().run_until_complete(test())
#asyncio.get_event_loop().run_forever()

