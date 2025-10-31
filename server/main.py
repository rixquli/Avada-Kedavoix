import time
from _thread import *
import os
import sys

# To import module from other folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from client.classes.player import Player
from client.classes.spell import Spell
from server.NetworkManager import NetworkManager
from server.message import Message, MessageType
from server.gameState import GameState

network = NetworkManager(is_server=True)
game_manager = GameState()


def handle_client(conn, player_id):
    print("Start Handle Player: ", player_id)

    initial_msg = Message(MessageType.CONNECT, {"player_id": player_id})
    conn.sendall(initial_msg.serialize())

    while True:
        try:
            # Attend de recevoir des message de ce player
            msg = network.receive_message(conn)

            if not msg:
                break

            # La liste des messages traités
            match msg.type:
                case MessageType.PLAYER_UPDATE:
                    # Cas où le joueur envoie sa position au serveur
                    player_data = msg.data
                    player = Player.from_dict(player_data)
                    game_manager.players.update(player_id, player)
                case MessageType.PLAYER_CAST_SPELL:
                    # Cas ou un joueur cast un spell
                    spell_id = msg.data["id"]
                    spell_data = msg.data["spell_data"]

                    # On peut récupérer l'objet spell directement a partir du json
                    spell = Spell.from_dict(spell_data)

                    game_manager.spells.addEntity(
                        spell,
                        fixed_id=spell_id,
                    )
                case MessageType.PLAYER_UPDATE_SPELL:
                    # Cas ou le joueur met a jour son spell
                    player_spells = msg.data
                    if player_spells:
                        for sid, spell_data in player_spells.items():
                            spell = Spell.from_dict(spell_data)
                            game_manager.spells.update(sid, spell)

        except Exception as e:
            print(f"Error with player {player_id}: {e}")
            break

    print(f"Lost connection with player {player_id}")
    game_manager.players.remove(player_id)
    if conn in network.player_connections:
        del network.player_connections[conn]
    conn.close()


def handle_conn():
    while True:
        # attend une nouvelle connection
        conn, addr = network.socket.accept()
        print(f"Connected to: {addr}")

        # Creer le joueur lors de sa connection
        num_players = len(game_manager.players.entities)
        colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]
        player_id = game_manager.players.addEntity(
            Player(
                x=50 + num_players * 100,
                y=50 + num_players * 50,
                color=colors[num_players % len(colors)],
                radius=10,
            )
        )

        network.player_connections[conn] = player_id
        print(f"Player {player_id} connected")
        start_new_thread(handle_client, (conn, player_id))


def broadcast_game_state():
    """Thread qui diffuse l'état du jeu à tous les clients"""
    while True:
        # TODO: Faire un update_all dans le game_manager
        for spell in list(game_manager.spells.entities.values()):
            spell.update()

        state = game_manager.get_game_state()
        msg = Message(MessageType.GAME_STATE, state)

        for conn in list(network.player_connections.keys()):
            try:
                conn.sendall(msg.serialize())
            except:
                pass

        time.sleep(1 / 30)  # 30 fois par seconde


def start_game_server(adress=None, port=None, max_player=5):
    network.start_server(adress, port, max_player=max_player)

    # Lance sur un autre thread la gestion des nouveauxjoueur
    start_new_thread(handle_conn, ())

    broadcast_game_state()


def main():
    start_game_server("localhost", 12345)


if __name__ == "__main__":
    main()
