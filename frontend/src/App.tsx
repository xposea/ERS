import React, { useState, useEffect, useRef } from 'react';

interface Player {
  id: number;
  name: string;
  websocket: WebSocket;
  messages: Message[];
}

interface Message {
  type: string;
  player?: string;
  player_count?: number;
  players?: string[];
  state?: any;
  winner?: string;
}

const App: React.FC = () => {
  const [players, setPlayers] = useState<Player[]>([]);
  const [playerName, setPlayerName] = useState('');
  const [lobbyId, setLobbyId] = useState('lobby1');
  const [playerCount, setPlayerCount] = useState(0);
  const [connected, setConnected] = useState(false);

  const addPlayer = (name: string) => {
    const websocket = new WebSocket(`ws://localhost:8000/ws/${lobbyId}/${name}`);
    const newPlayer: Player = { id: players.length, name, websocket, messages: [] };

    websocket.onopen = () => {
      console.log(`${name} connected to lobby ${lobbyId}`);
      setConnected(true);
      websocket.send(JSON.stringify({ type: 'join_lobby', lobby_id: lobbyId, player_name: name }));
    };

    websocket.onclose = () => {
      console.log(`${name} disconnected from lobby ${lobbyId}`);
      setConnected(false);
    };

    websocket.onmessage = (event) => {
      const message: Message = JSON.parse(event.data);
      if (message.type === 'player_joined' && message.player_count !== undefined) {
        setPlayerCount(message.player_count);
      }
      if (message.type === 'game_started' && message.players !== undefined) {
        console.log('Game started with players:', message.players);
      }
      newPlayer.messages.push(message);
      setPlayers([...players]);
    };

    websocket.onerror = (error) => {
      console.error(`WebSocket error for player ${name}:`, error);
    };

    setPlayers([...players, newPlayer]);
  };

  const joinLobby = () => {
    if (playerName.trim() !== '') {
      addPlayer(playerName.trim());
      setPlayerName('');
    }
  };

  const startGame = () => {
    players.forEach((player) => {
      if (player.websocket.readyState === WebSocket.OPEN) {
        player.websocket.send(JSON.stringify({ type: 'start_game', lobby_id: lobbyId }));
      }
    });
  };

  const playCard = (playerId: number) => {
    const player = players.find(p => p.id === playerId);
    if (player && player.websocket.readyState === WebSocket.OPEN) {
      player.websocket.send(JSON.stringify({ type: 'play', lobby_id: lobbyId }));
    }
  };

  const slap = (playerId: number) => {
    const player = players.find(p => p.id === playerId);
    if (player && player.websocket.readyState === WebSocket.OPEN) {
      player.websocket.send(JSON.stringify({ type: 'slap', lobby_id: lobbyId }));
    }
  };

  return (
    <div>
      <h1>Egyptian Ratscrew</h1>
      <div>
        <input
          type="text"
          value={playerName}
          onChange={(e) => setPlayerName(e.target.value)}
          placeholder="Enter player name"
        />
        <button onClick={joinLobby}>Join Lobby</button>
      </div>
      <div>
        <p>Lobby ID: {lobbyId}</p>
        <p>Players in Lobby: {playerCount}</p>
      </div>
      <button onClick={startGame} disabled={playerCount < 2}>Start Game</button>
      <div>
        {players.map((player) => (
          <div key={player.id} style={{ marginTop: '20px' }}>
            <h2>{player.name}</h2>
            <button onClick={() => playCard(player.id)} disabled={!connected}>Play Card</button>
            <button onClick={() => slap(player.id)} disabled={!connected}>Slap</button>
            <div>
              <h3>Messages</h3>
              <ul>
                {player.messages.map((message, index) => (
                  <li key={index}>{message.type}: {message.player || message.players?.join(', ')}</li>
                ))}
              </ul>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default App;
