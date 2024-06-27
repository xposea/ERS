import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const JoinLobbyScreen: React.FC = () => {
  const [playerName, setPlayerName] = useState('');
  const navigate = useNavigate();

  const joinLobby = () => {
    if (playerName.trim() !== '') {
      navigate(`/game/lobby1/${playerName}`);
    }
  };

  return (
    <div>
      <h1>Join Lobby</h1>
      <div>
        <input
          type="text"
          value={playerName}
          onChange={(e) => setPlayerName(e.target.value)}
          placeholder="Enter player name"
        />
        <button onClick={joinLobby}>Join Lobby</button>
      </div>
    </div>
  );
};

export default JoinLobbyScreen;
