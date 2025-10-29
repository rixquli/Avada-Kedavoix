# 🖥️ Server - Avada-Kedavoix

Ce dossier contient tout le code côté serveur du jeu.

## 📁 Structure

- **`main.py`** : Point d'entrée du serveur. Gère les connexions et le broadcast.
- **`NetworkManager.py`** : Abstraction des communications réseau (sockets).
- **`gameManager.py`** : Gère l'état global du jeu.
- **`message.py`** : Définit le protocole de communication (types de messages).
- **`managers/`** : Contient les gestionnaires spécialisés
  - **`playersManager.py`** : CRUD des joueurs (ajout, suppression, mise à jour)

## 🔧 Fonctionnement

### Point d'Entrée (`main.py`)

1. **Thread principal** : Broadcast de l'état du jeu (30 FPS)
   - Récupère l'état complet du jeu
   - Envoie à tous les clients connectés
   
2. **Thread de connexion** : Accepte les nouvelles connexions
   - Attend une connexion entrante
   - Crée un nouveau joueur
   - Lance un thread pour gérer ce joueur

3. **Threads par joueur** : Un thread par client connecté
   - Reçoit les mises à jour de position
   - Met à jour l'état du joueur côté serveur
   - Gère les déconnexions

### Network Manager (`NetworkManager.py`)

Abstraction des sockets qui peut fonctionner en mode :
- **Serveur** : Écoute les connexions
- **Client** : Se connecte au serveur

Méthodes principales :
- `start_server()` : Démarre le serveur
- `connect_to_server()` : Connexion client
- `send_message()` : Envoie un message sérialisé
- `receive_message()` : Reçoit et désérialise un message

### Game Manager (`gameManager.py`)

Contient l'état global du jeu :
- Instance de `PlayersManager`
- Méthode `get_game_state()` : Retourne l'état complet pour broadcast

### Players Manager (`managers/playersManager.py`)

Gère tous les joueurs :
- Dictionnaire `players` : {player_id: Player}
- `addPlayer()` : Crée un nouveau joueur avec un ID unique
- `removePlayer()` : Supprime un joueur déconnecté
- `updatePlayer()` : Met à jour la position d'un joueur
- `getOtherPlayers()` : Liste tous les joueurs sauf un

### Protocole de Messages (`message.py`)

Types de messages définis dans `MessageType` :
- `CONNECT` : Connexion initiale (serveur → client)
- `PLAYER_UPDATE` : Mise à jour position (client → serveur)
- `GAME_STATE` : État complet du jeu (serveur → clients)
- `DISCONNECT` : Déconnexion (non implémenté)
- `PLAYER_CAST_SPELL` : Lancement de sort (prévu)

## 🚀 Lancement

```bash
# Normal
python server\main.py

# Avec rechargement automatique (watchdog requis)
watchmedo auto-restart --patterns="*.py" --recursive -- python server\main.py
```

Le serveur écoute sur `localhost:12345`.

## 🔒 Architecture Thread-Safe

Le serveur utilise plusieurs threads :
- Thread principal pour le broadcast
- Thread d'acceptation des connexions
- Un thread par client connecté

⚠️ **Important** : Les accès concurrents au dictionnaire `players` ne sont pas protégés par des locks. Pour un environnement de production, il faudrait ajouter des `threading.Lock()`.

## 🎯 Améliorations Futures

- [ ] Ajouter des locks pour thread-safety
- [ ] Implémenter la gestion des sorts
- [ ] Ajouter de la validation des données reçues
- [ ] Système de rooms/lobbies
- [ ] Persistance des données (base de données)
- [ ] Rate limiting pour éviter le spam
- [ ] Heartbeat pour détecter les clients déconnectés
