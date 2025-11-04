import time
from _thread import *
import os
import sys


# To import module from other folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from client.classes.pnj import PNJ
from client.classes.enemy import Enemy
from client.classes.player import Player
from client.classes.spell import Spell
from server.NetworkManager import NetworkManager
from server.message import Message, MessageType
from server.gameState import GameState

network = NetworkManager(is_server=True)
game_state = GameState()


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
                    game_state.players.update(player_id, player)
                case MessageType.PLAYER_CAST_SPELL:
                    # Cas ou un joueur cast un spell
                    spell_id = msg.data["id"]
                    spell_data = msg.data["spell_data"]

                    # On peut récupérer l'objet spell directement a partir du json
                    spell = Spell.from_dict(spell_data)

                    game_state.spells.addEntity(
                        spell,
                        fixed_id=spell_id,
                    )
                case MessageType.PLAYER_UPDATE_SPELL:
                    # Cas ou le joueur met a jour son spell
                    player_spells = msg.data
                    if player_spells:
                        for sid, spell_data in player_spells.items():
                            spell = Spell.from_dict(spell_data)
                            game_state.spells.update(sid, spell)

        except Exception as e:
            print(f"Error with player {player_id}: {e}")
            break

    print(f"Lost connection with player {player_id}")
    game_state.players.remove(player_id)
    if conn in network.player_connections:
        del network.player_connections[conn]
    conn.close()


def handle_conn():
    while True:
        # attend une nouvelle connection
        conn, addr = network.socket.accept()
        print(f"Connected to: {addr}")

        # Creer le joueur lors de sa connection
        num_players = len(game_state.players.entities)
        colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]
        player_id = game_state.players.addEntity(
            Player(
                x=num_players * 100,
                y=num_players * 50,
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
        # Les joueurs s'update coté client
        game_state.update_all()

        state = game_state.get_game_state()
        msg = Message(MessageType.GAME_STATE, state)

        for conn in list(network.player_connections.keys()):
            try:
                conn.sendall(msg.serialize())
            except:
                pass

        time.sleep(1 / 30)  # 30 fois par seconde


# TODO: Enlever cette fonction elle ne doit rester que en développement ou etre adapté
def spawn_element_at_start():
    enemy1 = game_state.enemies.addEntity(Enemy(200, 200, (0, 255, 255)))
    enemy2 = game_state.enemies.addEntity(Enemy(350, 350, (0, 255, 255)))

    pnj1 = game_state.pnjs.addEntity(PNJ(-150, -150, (255, 0, 255)))


def start_game_server(adress=None, port=None, max_player=5, is_solo=False):
    network.start_server(adress, port, max_player=max_player, is_solo=is_solo)

    # Lance sur un autre thread la gestion des nouveauxjoueur
    start_new_thread(handle_conn, ())

    # Fais apparaitre les éléments au demarage de la partie
    spawn_element_at_start()

    # Envoie l'etat du monde aux joueurs
    broadcast_game_state()


def main():
    start_game_server("0.0.0.0", 12345)


if __name__ == "__main__":
    main()
