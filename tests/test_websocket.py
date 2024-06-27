import asyncio
import websockets
import json
import logging
import aiohttp
import random


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


async def player_actions(uri, player_name):
    async with websockets.connect(uri) as websocket:
        logger.info(f"{player_name} connected to lobby")

        await websocket.send(json.dumps({"type": "join_lobby"}))
        logger.info(f"{player_name} sent join_lobby request")

        game_started = False
        while True:
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=60.0)
                logger.info(f"{player_name} received: {response}")
                response_data = json.loads(response)

                if response_data['type'] == 'game_started':
                    game_started = True
                elif response_data['type'] == 'game_state':
                    if game_started and response_data['state']['current_player'] == player_name:
                        # It's this player's turn, so play a card
                        await asyncio.sleep(0.5)  # Random delay
                        await websocket.send(json.dumps({"type": "play"}))
                        # logger.info(f"{player_name} played a card")
                elif response_data['type'] == 'slap_opportunity':
                    # Decide whether to slap (you can adjust this probability)
                    if random.random() < 0.5:  # 50% chance to slap
                        await asyncio.sleep(random.uniform(0.1, 0.2))  # Random delay
                        await websocket.send(json.dumps({"type": "slap"}))
                        # logger.info(f"{player_name} attempted to slap")
                    # else:
                        # logger.info(f"{player_name} decided not to slap")
                elif response_data['type'] == 'game_over':
                    logger.info(f"Game is over. Winner is {response_data['winner']}.")
                    break
                # Add more elif conditions for other message types if needed

            except asyncio.TimeoutError:
                logger.warning(f"{player_name}: No response from server for 60 seconds")
            except websockets.exceptions.ConnectionClosed as e:
                logger.error(f"{player_name}: WebSocket connection closed: {e}")
                break

    logger.info(f"{player_name} disconnected from lobby")


async def start_game(uri):
    async with websockets.connect(uri) as websocket:
        await asyncio.sleep(5)
        logger.info("Sending start_game command")
        await websocket.send(json.dumps({"type": "start_game"}))
        try:
            response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
            logger.info(f"Start game response: {response}")
            # Process the response...
        except asyncio.TimeoutError:
            logger.warning("Start game: No response from server for 10 seconds")
        except websockets.exceptions.ConnectionClosed:
            logger.error("Start game: WebSocket connection closed")


async def game_session(lobby_id, players):
    if not await check_server_health():
        logger.error("Server is not healthy. Aborting game session.")
        return

    player_tasks = [player_actions(f"ws://localhost:8000/ws/{lobby_id}/{i}", f"{i}") for i in
                    players]
    start_game_task = start_game(f"ws://localhost:8000/ws/{lobby_id}/starter")
    await asyncio.gather(start_game_task, *player_tasks)


async def multiple_games():

    session1 = asyncio.create_task(game_session("test_lobby", ['p1', 'p2']))  # Start a game with 3 players
    session2 = asyncio.create_task(game_session("test_lobby2", ['p3', 'p4']))
    await asyncio.gather(session1, session2)


if __name__ == '__main__':
    asyncio.run(multiple_games())


# TODO Player disconnecting when waiting too long. Fix game over but other player keeps going.
