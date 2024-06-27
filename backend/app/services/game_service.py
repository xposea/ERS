import time
from game_logic.game import ERSGame


class GameService:
    def __init__(self):
        self.lobbies = {}
        self.games = {}
        self.last_play_time = {}

    def create_lobby(self, lobby_id):
        if lobby_id not in self.lobbies:
            self.lobbies[lobby_id] = set()
        return lobby_id

    def join_lobby(self, lobby_id, player_name):
        if lobby_id not in self.lobbies:
            self.create_lobby(lobby_id)
        self.lobbies[lobby_id].add(player_name)
        return len(self.lobbies[lobby_id])

    def start_game(self, lobby_id):
        if lobby_id in self.lobbies and len(self.lobbies[lobby_id]) >= 2:
            players = list(self.lobbies[lobby_id])
            game = ERSGame(players)
            game.start_game()
            self.games[lobby_id] = game
            del self.lobbies[lobby_id]
            self.last_play_time[lobby_id] = time.time()
            print(players)
            return game, None
        return None, "Not enough players to start the game"

    def play_turn(self, lobby_id, player_name):
        game = self.games.get(lobby_id)
        if game and game.current_player.name == player_name:
            try:
                winner = game.play_turn()
                self.last_play_time[lobby_id] = time.time()
                if winner:
                    return True, "game_over", winner.name
                return True, "turn_played", None
            except Exception as e:
                print(f"Error during play_turn: {str(e)}")
                return False, "error", str(e)
        return False, "invalid_turn", None

    def attempt_slap(self, lobby_id, player_name):
        game = self.games.get(lobby_id)
        if game:
            player = next((p for p in game.players if p.name == player_name), None)
            if player:
                success = game.attempt_slap(player)
                current_time = time.time()
                slap_time = current_time - self.last_play_time.get(lobby_id, current_time)
                return success, slap_time
        return False, 0

    def can_slap(self, lobby_id):
        game = self.games.get(lobby_id)
        return game.can_players_slap() if game else False

    def get_state(self, lobby_id):
        game = self.games.get(lobby_id)
        if game:
            winner = game.get_winner()
            return {
                "current_player": game.current_player.name,
                "pile_count": len(game.pile),
                "players": [{"name": p.name, "card_count": p.card_count()} for p in game.players],
                "is_game_over": game.is_game_over(),
                "winner": winner.name if winner else None
            }
        return {}

    # def remove_player(self, lobby_id, player_name):
    #     if lobby_id in self.lobbies:
    #         self.lobbies[lobby_id].discard(player_name)
    #         if not self.lobbies[lobby_id]:
    #             del self.lobbies[lobby_id]
    #     elif lobby_id in self.games:
    #         game = self.games[lobby_id]
    #         player = next((p for p in game.all_players if p.name == player_name), None)
    #         if player:
    #             game.remove_player(player)
    #         if game.is_game_over():
    #             del self.games[lobby_id]
