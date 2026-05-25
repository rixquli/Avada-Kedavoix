"""
Point d'entrée du serveur et gere les different client en receptionnant les requete et en envoyant
une copie du monde a tout les clients

De plus,
"python server/main.py" permet de lancer juste un serveur rejoingnable en entrant son ip local
"""

import pickle
import time
from _thread import start_new_thread
import socket
import os
import sys

import uuid

from server.gameState import GameState

# To import module from other folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from server.classes.saver import Saver
from client.layerList import Layer
from client.classes.wall import Wall
from client.classes.pnj import PNJ
from client.classes.enemy import Enemy, EnemyList
from client.classes.player import Player
from client.classes.spell import Spell
from client.classes.house import House
from server.NetworkManager import NetworkManager
from server.message import Message, MessageType

network = NetworkManager()
network.setup(is_server=True)
saver = Saver(network)
SAVE_DELAY = 60  # delay de sauvegarde en seconde


def handle_client(conn: socket.socket, player_id: str):
    print("Start Handle Player: ", player_id)

    initial_msg = Message(MessageType.CONNECT, {"player_id": player_id})
    conn.sendall(initial_msg.serialize())

    while True:
        try:
            # Attend de recevoir des message de ce player
            msg = network.receive_message(conn)

            if not msg:
                break
            msg_t = msg.as_typed()

            # La liste des messages traités
            match msg_t["type"]:
                case MessageType.PLAYER_UPDATE:
                    # Cas où le joueur envoie sa position au serveur
                    player_data = msg.data
                    # player = Player.from_dict(player_data)
                    network.game_state.players.update(player_id, player_data)
                case MessageType.PLAYER_CAST_SPELL:
                    # Cas ou un joueur cast un spell
                    spell_id = msg.data["id"]
                    spell_data = msg.data["spell_data"]

                    # On peut récupérer l'objet spell directement a partir du json
                    spell = Spell.from_dict(spell_data)

                    network.game_state.spells.addEntity(
                        spell,
                        fixed_id=spell_id,
                    )
                case MessageType.PLAYER_UPDATE_SPELL:
                    # Cas ou le joueur met a jour son spell
                    player_spells = msg.data
                    if player_spells:
                        for sid, spell_data in player_spells.items():
                            spell = Spell.from_dict(spell_data)
                            network.game_state.spells.update(sid, spell)
                case MessageType.PLAYER_HEAL:
                    player_id = msg.data["id"]
                    player = network.game_state.players.get(player_id)
                    if player:
                        player.heal()
                case MessageType.CHANGE_LAYER:
                    player = network.game_state.players.get(player_id)
                    if player:
                        player.world_layer = msg.data["layer"]
                        player.invinsibility_timer = 2
                    layer_state = network.game_state.get_game_state(
                        diff=False, layer=msg.data["layer"]
                    )
                    msg = Message(MessageType.CHANGE_LAYER, layer_state)
                    data = msg.serialize()
                    conn.sendall(data)

        except Exception as e:
            print(f"Error with player {player_id}: {e}")
            break

    print(f"Lost connection with player {player_id}")
    network.game_state.players.remove(player_id)
    if conn in network.player_connections:
        del network.player_connections[conn]
    conn.close()


def handle_conn():
    while True:
        # attend une nouvelle connection
        conn, addr = network.socket.accept()
        print(f"Connected to: {addr}")

        # Creer le joueur lors de sa connection
        num_players = len(network.game_state.players.entities)
        colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]
        player_id = f"P{uuid.getnode()}"

        # si le joueur sur la meme machine est deja connecter alors on creer une deuxieme instance
        if (
            player_id in network.player_connections.values()
            and network.game_state.players.exist(player_id)
        ):
            i = 2
            test_player_id = player_id + f"_{i}"
            while network.game_state.players.exist(test_player_id):
                i += 1
                test_player_id = player_id + f"_{i}"
            player_id = test_player_id

        if not network.game_state.players.exist(player_id):
            network.game_state.players.addEntity(
                Player(
                    x=num_players * 100,
                    y=num_players * 50,
                    color=colors[num_players % len(colors)],
                    radius=10,
                    is_server=True,
                    world_layer=1,
                ),
                fixed_id=player_id,
            )

        print(f"Player {player_id} connected")

        # Envoi synchronisé du CONNECT + snapshot complet au nouveau client
        try:
            initial_msg = Message(MessageType.CONNECT, {"player_id": player_id})
            conn.sendall(initial_msg.serialize())

            full_state = network.game_state.get_game_state(
                diff=False, layer=network.game_state.players.get(player_id).world_layer
            )
            full_msg = Message(MessageType.GAME_STATE, full_state)
            conn.sendall(full_msg.serialize())
            full_msg = Message(MessageType.DUNGEON_DATA, network.Dungeon.dungeonWalls)
            conn.sendall(full_msg.serialize())

            # Ajouter le client au broadcast uniquement après l'envoi du snapshot complet.
            network.player_connections[conn] = player_id
        except Exception as e:
            print(f"Failed to send initial data to {player_id}: {e}")

        start_new_thread(handle_client, (conn, player_id))


def broadcast_game_state():
    """Thread qui diffuse l'état du jeu à tous les clients"""
    counter = 0
    while True:
        # Les joueurs s'update coté client
        # network.game_state.update_all()

        time_in_min = int(network.game_state.ingame_time // 60)
        is_night = (
            time_in_min % (GameState.day_min + GameState.night_min) >= GameState.day_min
        )

        if not is_night:
            network.night_spawned_surface = False
        else:
            # si nuit et pas encore spawnée -> vérifier s'il y a au moins un joueur sur la layer 1
            if not network.night_spawned_surface:
                players_on_layer1 = [
                    p
                    for p in network.game_state.players.get_list()
                    if p.world_layer == Layer.OVERWORLD.value or p.world_layer == 1
                ]
                if players_on_layer1:
                    import random

                    spawn_count = random.randint(2, 3)
                    network.enemySpawner.spawn_night_surface(
                        world_layer=1, count=spawn_count
                    )
                    network.night_spawned_surface = True

        layersToRender = []
        for player in network.game_state.players.get_list():
            layer = player.world_layer
            if layer not in layersToRender:
                layersToRender.append(layer)
                network.game_state.update_all_layer(layer)

        state_by_layer = {}
        for layer in layersToRender:
            state_by_layer[layer] = network.game_state.get_game_state(
                diff=True, layer=layer
            )
        # state = network.game_state.get_game_state(diff=True)

        for conn in list(network.player_connections.keys()):
            try:
                player = network.game_state.players.get(
                    network.player_connections[conn]
                )
                player_layer = player.world_layer
                pending_event = player.pending_network_event
                if pending_event:
                    if pending_event["type"] == "respawn":
                        player.world_layer = pending_event["layer"]
                        layer_state = network.game_state.get_game_state(
                            diff=False, layer=pending_event["layer"]
                        )
                        msg = Message(MessageType.PLAYER_RESPAWN, layer_state)
                        data = msg.serialize()
                        conn.sendall(data)
                    player.pending_network_event = None
                else:
                    msg = Message(MessageType.GAME_STATE, state_by_layer[player_layer])
                    data = msg.serialize()
                    conn.sendall(data)
            except:
                pass

        time.sleep(1 / 30)  # 30 fois par seconde
        counter += 1
        if counter > 30 * SAVE_DELAY:
            counter = 0
            saver.save()


def generate_all_dungeon():
    network.Dungeon.generate_all_layer()
    for i, e in enumerate(network.Dungeon.dungeonWalls):
        for data in e.walls:
            wall = Wall(
                data[0],
                data[1],
                data[2],
                data[3],
                Layer.DUNGEON_BASE.value + i,
                texture_path=None,
            )
            network.game_state.walls.addEntity(wall)
            network.game_state.collision_manager.client_collider_groups["obstacle"].add(
                wall
            )
        network.enemySpawner.dungeon_generate(Layer.DUNGEON_BASE.value + i, i)


# TODO: Enlever cette fonction elle ne doit rester que en développement ou etre adapté
def spawn_element_at_start():
    # enemy1 = network.game_state.enemies.addEntity(
    #     Enemy.get_enemy_type(
    #         EnemyList.GOBELIN_MASSUE, x=200, y=200, world_layer=1, is_server=True
    #     )
    # )
    # enemy2 = network.game_state.enemies.addEntity(
    #     Enemy.get_enemy_type(
    #         EnemyList.BOSS, x=350, y=350, world_layer=1, is_server=True
    #     )
    # )
    # enemy2 = network.game_state.enemies.addEntity(
    #     Enemy(350, 350, (0, 255, 255), world_layer=2, is_server=True)
    # )

    # TODO: deplacer les texts a l'exterieur du programme
    pnj1 = network.game_state.pnjs.addEntity(
        PNJ(
            -50,
            50,
            (255, 0, 255),
            text=[
                {
                    "name": "Le joueur",
                    "text": "Bonjour, sauriez vous comment apprendre un nouveau sort ?",
                },
                {
                    "name": "Boulanger",
                    "text": "Je ne sais pas… Mais je crois me souvenir qu’un sorcier autrefois m'avait donné un parchemin que je n’ai jamais pu déchiffrer, peut-être qu’il t'intéressera.",
                },
                {
                    "name": "Boulanger",
                    "text": "Si tu arrives à trouver un moyen de le traduire, je te le donnerai",
                },
                {
                    "name": "Boulanger",
                    "text": "Enfonce toi dans le labyrinthe de la tour, déchiffre le message et ramène moi les indices qui t'ont aidé. Alors peut-être tu développera de nouvelles compétences.",
                },
                {
                    "name": "Le joueur",
                    "text": "Ça semble dangereux… mais je suis prêt.",
                },
                {
                    "name": "Boulanger",
                    "text": "Bien. Fais preuve de courage et de sagesse.",
                },
            ],
            is_server=True,
        )
    )
    pnj2 = network.game_state.pnjs.addEntity(
        PNJ(
            -250,
            10,
            (255, 0, 255),
            text=[
                {
                    "name": "Le joueur",
                    "text": "Bonjour, sauriez vous comment apprendre un nouveau sort ?",
                },
                {
                    "name": "Boulanger",
                    "text": "Je ne sais pas… Mais je crois me souvenir qu’un sorcier autrefois m'avait donné un parchemin que je n’ai jamais pu déchiffrer, peut-être qu’il t'intéressera.",
                },
                {
                    "name": "Boulanger",
                    "text": "Si tu arrives à trouver un moyen de le traduire, je te le donnerai",
                },
                {
                    "name": "Boulanger",
                    "text": "Enfonce toi dans le labyrinthe de la tour, déchiffre le message et ramène moi les indices qui t'ont aidé. Alors peut-être tu développera de nouvelles compétences.",
                },
                {
                    "name": "Le joueur",
                    "text": "Ça semble dangereux… mais je suis prêt.",
                },
                {
                    "name": "Boulanger",
                    "text": "Bien. Fais preuve de courage et de sagesse.",
                },
            ],
            is_server=True,
        )
    )
    
    house1 = House(-80, -100, 20, 1, True)
    network.game_state.houses.addEntity(
        house1
    )
    network.game_state.collision_manager.client_collider_groups["obstacle"].add(house1.hitbox)
    
    house2 = House(-300, -120, 20, 1, True)
    network.game_state.houses.addEntity(
        house2
    )
    network.game_state.collision_manager.client_collider_groups["obstacle"].add(house2.hitbox)

    house3 = House(400, 150, 20, 1, True)
    network.game_state.houses.addEntity(
        house3
    )
    network.game_state.collision_manager.client_collider_groups["obstacle"].add(house3.hitbox)

    
    walls = [
        Wall(-500, -500, 1000, 50, texture_path=None),
        Wall(-500, 500, 1050, 50, texture_path=None),
        Wall(-500, -500, 50, 1000, texture_path=None),
        Wall(500, -500, 50, 1000, texture_path=None),
        Wall(100, 100, 100, 50, texture_path=None),
    ]
    for wall in walls:
        network.game_state.walls.addEntity(wall)
        network.game_state.collision_manager.client_collider_groups["obstacle"].add(
            wall
        )
    start_new_thread(generate_all_dungeon, ())
    """
    network.Dungeon.generate_all_layer()
    print(network.Dungeon.dungeonWalls[0])
    for i, e in enumerate(network.Dungeon.dungeonWalls):
        print(i, e)
        for data in e.walls:
            wall = Wall(
                data[0],
                data[1],
                data[2],
                data[3],
                Layer.DUNGEON_BASE.value + i,
                texture_path=None,
            )
            network.game_state.walls.addEntity(wall)
            network.game_state.collision_manager.client_collider_groups["obstacle"].add(
                wall
            )
        network.enemySpawner.dungeon_generate(Layer.DUNGEON_BASE.value + i, i)
    """


def start_game_server(
    adress=None, port=None, max_player=5, is_solo=False, newGame=True
):
    network.start_server(adress, port, max_player=max_player, is_solo=is_solo)

    # Fais apparaitre les éléments au demarage de la partie
    load_ok = False
    if not newGame:
        load_ok = saver.load_save()

    if newGame or not load_ok:
        spawn_element_at_start()

    # Lance sur un autre thread la gestion des nouveaux joueur
    # apres le chargement pour eviter d'ecraser les positions de sauvegarde.
    start_new_thread(handle_conn, ())

    # Envoie l'etat du monde aux joueurs
    broadcast_game_state()


def manual_save():
    saver.save()


def main():
    from client.gameManager import GameManager

    game_manager = GameManager()
    game_manager.setup_server()

    start_game_server("0.0.0.0", 12345)


if __name__ == "__main__":
    main()
