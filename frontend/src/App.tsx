import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import JoinLobbyScreen from './JoinLobbyScreen';
import GameScreen from './GameScreen';

const App: React.FC = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<JoinLobbyScreen />} />
        <Route path="/game/:lobbyId/:playerName" element={<GameScreen />} />
      </Routes>
    </Router>
  );
};

export default App;
