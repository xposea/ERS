# game_service.py

from typing import Dict, Set, Tuple, Optional
from game_logic.game import ERSGame  # Assuming you have an ERSGame class implemented


class GameService:
    def __init__(self):
        self.lobbies: Dict[str, Set[str]] = {}  # lobby_id -> set of player names
        self.games: Dict[str, ERSGame] = {}  # lobby_id -> ERSGame instance

    def create_lobby(self, lobby_id: str) -> bool:
        """Create a new lobby if it doesn't exist."""
        if lobby_id not in self.lobbies:
            self.lobbies[lobby_id] = set()
            return True
        return False

    def join_lobby(self, lobby_id: str, player_name: str) -> bool:
        """Add a player to a lobby."""
        if lobby_id in self.lobbies:
            self.lobbies[lobby_id].add(player_name)
            return True
        return False

    def leave_lobby(self, lobby_id: str, player_name: str) -> bool:
        """Remove a player from a lobby."""
        if lobby_id in self.lobbies and player_name in self.lobbies[lobby_id]:
            self.lobbies[lobby_id].remove(player_name)
            if len(self.lobbies[lobby_id]) == 0:
                del self.lobbies[lobby_id]
            return True
        return False

    def start_game(self, lobby_id: str) -> Tuple[Optional[ERSGame], Optional[str]]:
        """Start a game for a given lobby."""
        if lobby_id not in self.lobbies:
            return None, "Lobby does not exist"
        if len(self.lobbies[lobby_id]) < 2:
            return None, "Not enough players to start the game"
        players = list(self.lobbies[lobby_id])
        game = ERSGame(players)
        game.start_game()
        self.games[lobby_id] = game
        del self.lobbies[lobby_id]
        return game, None

    def get_game(self, lobby_id: str) -> Optional[ERSGame]:
        """Get the game instance for a given lobby."""
        return self.games.get(lobby_id)

    def play_turn(self, lobby_id: str, player_name: str) -> bool:
        """Play a turn for a given player in a game."""
        game = self.get_game(lobby_id)
        if game and game.current_player.name == player_name:
            game.play_turn()
            return True
        return False

    def attempt_slap(self, lobby_id: str, player_name: str) -> bool:
        """Attempt a slap for a given player in a game."""
        game = self.get_game(lobby_id)
        if game:
            return game.attempt_slap(player_name)
        return False

    def can_slap(self, lobby_id: str) -> bool:
        """Check if slapping is currently allowed in a game."""
        game = self.get_game(lobby_id)
        if game:
            return game.can_players_slap()
        return False

    def get_state(self, lobby_id: str) -> dict:
        """Get the current state of a game."""
        game = self.get_game(lobby_id)
        if game:
            return {
                "current_player": game.current_player.name,
                "pile_count": len(game.pile),
                "players": [{"name": p.name, "card_count": p.card_count()} for p in game.players],
                "is_game_over": game.is_game_over(),
                "winner": game.get_winner().name if game.get_winner() else None
            }
        return {}

    def remove_player(self, lobby_id: str, player_name: str) -> None:
        """Remove a player from a lobby or game."""
        if lobby_id in self.lobbies:
            self.leave_lobby(lobby_id, player_name)
        elif lobby_id in self.games:
            game = self.games[lobby_id]
            game.remove_player(player_name)
            if game.is_game_over():
                del self.games[lobby_id]

    def get_lobby_players(self, lobby_id: str) -> Set[str]:
        """Get the set of players in a lobby."""
        return self.lobbies.get(lobby_id, set())

    def lobby_exists(self, lobby_id: str) -> bool:
        """Check if a lobby exists."""
        return lobby_id in self.lobbies

    def game_exists(self, lobby_id: str) -> bool:
        """Check if a game exists for a given lobby."""
        return lobby_id in self.games
