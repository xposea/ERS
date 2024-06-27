import asyncio
import websockets
import json
import logging
import aiohttp
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_server_health():
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get('http://localhost:8000') as response:
                if response.status == 200:
                    logger.info("Server is healthy")
                    return True
                else:
                    logger.error(f"Server health check failed with status {response.status}")
                    return False
        except aiohttp.ClientError as e:
            logger.error(f"Failed to connect to server: {str(e)}")
            return False

async def player_actions(uri, player_name, actions_queue):
    async with websockets.connect(uri) as websocket:
        logger.info(f"{player_name} connected to lobby")

        await websocket.send(json.dumps({"type": "join_lobby"}))
        logger.info(f"{player_name} sent join_lobby request")

        game_started = False
        while True:
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                logger.info(f"{player_name} received: {response}")
                response_data = json.loads(response)

                if response_data['type'] == 'game_started':
                    game_started = True
                elif response_data['type'] == 'game_state':
                    if game_started and response_data['state']['current_player'] == player_name:
                        # It's this player's turn, so play a card if queued
                        if not actions_queue.empty():
                            action = await actions_queue.get()
                            if action == 'play':
                                await websocket.send(json.dumps({"type": "play"}))
                                logger.info(f"{player_name} played a card")
                elif response_data['type'] == 'slap_opportunity':
                    # Attempt to slap if queued
                    if not actions_queue.empty():
                        action = await actions_queue.get()
                        if action == 'slap':
                            await websocket.send(json.dumps({"type": "slap"}))
                            logger.info(f"{player_name} attempted to slap")

            except asyncio.TimeoutError:
                logger.warning(f"{player_name}: No response from server for 30 seconds")
            except websockets.exceptions.ConnectionClosed as e:
                logger.error(f"{player_name}: WebSocket connection closed: {e}")
                break

async def start_game(uri):
    async with websockets.connect(uri) as websocket:
        await asyncio.sleep(5)
        logger.info("Sending start_game command")
        await websocket.send(json.dumps({"type": "start_game"}))

        while True:
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                logger.info(f"Start game response: {response}")
                # Process the response...
            except asyncio.TimeoutError:
                logger.warning("Start game: No response from server for 10 seconds")
            except websockets.exceptions.ConnectionClosed:
                logger.error("Start game: WebSocket connection closed")
                break

async def read_actions(actions_queues):
    while True:
        action = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
        action = action.strip()
        if len(action) == 2 and action[0].isdigit() and action[1] in ('p', 's'):
            player_num = int(action[0]) - 1
            act_type = 'play' if action[1] == 'p' else 'slap'
            if 0 <= player_num < len(actions_queues):
                await actions_queues[player_num].put(act_type)
            else:
                logger.warning("Invalid player number")
        else:
            logger.warning("Invalid action format. Use '1p' or '1s' etc.")

async def game_session(lobby_id, num_players=2):
    if not await check_server_health():
        logger.error("Server is not healthy. Aborting game session.")
        return

    actions_queues = [asyncio.Queue() for _ in range(num_players)]
    player_tasks = [player_actions(f"ws://localhost:8000/ws/{lobby_id}/player{i+1}", f"player{i+1}", actions_queues[i]) for i in range(num_players)]
    start_game_task = start_game(f"ws://localhost:8000/ws/{lobby_id}/starter")
    actions_reader_task = read_actions(actions_queues)
    await asyncio.gather(start_game_task, actions_reader_task, *player_tasks)

if __name__ == "__main__":
    asyncio.run(game_session("test_lobby", 2))  # Start a game with 2 players
