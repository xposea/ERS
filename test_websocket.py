import asyncio
import websockets
import json


async def test_game():
    uri = "ws://localhost:8000/ws/lobby1/player1"
    async with websockets.connect(uri) as websocket:
        # Join lobby
        print("Connected to lobby")

        # Wait for a moment
        await asyncio.sleep(1)

        # Start game
        await websocket.send(json.dumps({"type": "start_game"}))
        print("Sent start_game command")

        # Receive messages
        while True:
            response = await websocket.recv()
            print(f"Received: {response}")

asyncio.get_event_loop().run_until_complete(test_game())
