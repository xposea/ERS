import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';

interface Message {
  type: string;
  player?: string;
  player_count?: number;
  players?: string[];
  state?: any;
  winner?: string;
}

interface Player {
  id: number;
  name: string;
}

const GameScreen: React.FC = () => {
  const { lobbyId, playerName } = useParams<{ lobbyId: string; playerName: string }>();
  const [websocket, setWebsocket] = useState<WebSocket | null>(null);
  const [playerCount, setPlayerCount] = useState(0);
  const [players, setPlayers] = useState<Player[]>([]);

  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8000/ws/${lobbyId}/${playerName}`);
    setWebsocket(ws);

    ws.onopen = () => {
      console.log(`${playerName} connected to lobby ${lobbyId}`);
      ws.send(JSON.stringify({ type: 'join_lobby', lobby_id: lobbyId, player_name: playerName }));
    };

    ws.onclose = () => {
      console.log(`${playerName} disconnected from lobby ${lobbyId}`);
    };

    ws.onmessage = (event) => {
      const message: Message = JSON.parse(event.data);
      if (message.type === 'player_joined' && message.player_count !== undefined) {
        setPlayerCount(message.player_count);
      }
      if (message.type === 'game_started' && message.players !== undefined) {
        setPlayers(message.players.map((name, index) => ({ id: index, name })));
      }
    };

    ws.onerror = (error) => {
      console.error(`WebSocket error for player ${playerName}:`, error);
    };

    return () => {
      ws.close();
    };
  }, [lobbyId, playerName]);

  const startGame = () => {
    websocket?.send(JSON.stringify({ type: 'start_game', lobby_id: lobbyId }));
  };

  const playCard = () => {
    websocket?.send(JSON.stringify({ type: 'play', lobby_id: lobbyId }));
  };

  const slap = () => {
    websocket?.send(JSON.stringify({ type: 'slap', lobby_id: lobbyId }));
  };

  return (
    <div>
      <h1>Game Lobby: {lobbyId}</h1>
      <p>Player: {playerName}</p>
      <p>Players in Lobby: {playerCount}</p>
      {playerCount < 2 ? (
        <button onClick={startGame} disabled>
          Start Game (Waiting for more players)
        </button>
      ) : (
        <button onClick={startGame}>Start Game</button>
      )}
      <div>
        <h2>Players</h2>
        <ul>
          {players.map((player) => (
            <li key={player.id}>{player.name}</li>
          ))}
        </ul>
      </div>
      <div>
        <button onClick={playCard}>Play Card</button>
        <button onClick={slap}>Slap</button>
      </div>
    </div>
  );
};

export default GameScreen;
