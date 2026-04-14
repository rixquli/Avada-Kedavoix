# Avada-Kedavoix 🎮✨

## 📝 Description

Avada-Kedavoix est un jeu multijoueur en temps réel développé en Python avec Pygame. Les joueurs incarnent des magiciens et peuvent se déplacer dans un environnement 2D, lancer des sorts et interagir avec d'autres joueurs via une architecture client-serveur robuste. Le jeu supporte aussi la reconnaissance vocale pour les commandes.

## ✨ Fonctionnalités

- 🎮 Jeu multijoueur en temps réel avec synchronisation serveur
- 🌐 Architecture client-serveur avec sockets TCP/IP
- 🎨 Interface graphique avec Pygame et système d'UI custom
- 👥 Support de plusieurs joueurs simultanés avec gestion des connexions/déconnexions
- 🎯 Système de mouvements fluides (ZQSD ou flèches directionnelles)
- 🔄 Synchronisation automatique de l'état du jeu entre clients (broadcast 30 FPS)
- 🔮 Système de sorts avec cooldown et animation
- 🗺️ Carte générative avec obstacles, PNJs et ennemis
- 🎤 Reconnaissance vocale en français pour commandes alternatives
- ⚔️ Système de collisions avec hitbox
- 🎬 Animations fluides pour les personnages (marche, course, attaque, dégâts, mort)

## 📋 Librairies

- Python 3.10 ou supérieur
- pygame>=2.5.0
- vosk (reconnaissance vocale)
- sounddevice (audio pour vosk)
- pytmx (parsage des cartes Tiled)

## 🚀 Installation

1. **Clonez le dépôt** :

```bash
git clone https://github.com/rixquli/Avada-Kedavoix.git
cd Avada-Kedavoix
```

1. **Installez les dépendances** :

```bash
pip install -r requirements.txt
```

## 🎯 Utilisation

### Démarrer le serveur

Dans un terminal, lancez le serveur :

```bash
python server/main.py
```

Le serveur démarre sur `localhost:12345` et attend les connexions des clients.

### Démarrer un ou plusieurs clients

Dans d'autres terminaux (ou plusieurs pour simuler plusieurs joueurs), lancez le client :

```bash
python client/main.py
```

Chaque client se connectera automatiquement au serveur (ou lancera son propre serveur en mode solo).

### Contrôles

**Clavier :**

- **Déplacement** : `Z` `Q` `S` `D` ou flèches directionnelles
  - ⬆️ Haut : `Z`
  - ⬇️ Bas : `S`
  - ⬅️ Gauche : `Q`
  - ➡️ Droite : `D`
- **Sort basique** : `Clic gauche`
- **Commandes vocales** : Parlez en français pour contrôler le jeu

**Reconnaissance vocale :**

- Dites "spell" pour lancer un sort

## 🏗️ Architecture du Projet

``` txt
avada-kedavoix/
├── client/                          # Code côté client (client-serveur)
│   ├── main.py                     # Point d'entrée du client
│   ├── clientManager.py            # Gestion de la connexion et des messages réseau
│   ├── gameManager.py              # Gestion globale du jeu (singleton)
│   ├── menus.py                    # Menus (main, join, host)
│   ├── utils.py                    # Fonctions utilitaires
│   ├── classes/
│   │   ├── player.py               # Classe Player avec animations et mouvements
│   │   ├── enemy.py                # Classe Enemy avec IA
│   │   ├── pnj.py                  # PNJs (personnages non joueurs)
│   │   ├── spell.py                # Système de sorts avec hitbox
│   │   ├── wall.py                 # Obstacles et murs
│   │   ├── mapBackground.py        # Fond de carte
│   │   ├── animator.py             # Système d'animations
│   │   └── hitbox.py               # Gestion des collisions
│   ├── ui/
│   │   ├── UI.py                   # Gestionnaire d'interface
│   │   ├── button.py               # Composant bouton
│   │   ├── text.py                 # Composant texte
│   │   ├── textInput.py            # Champ de saisie
│   │   └── uiUtils.py              # Utilitaires UI
│   ├── enums/
│   │   └── anchor.py               # Énumération anchor (positionnement UI)
│   ├── voice/
│   │   ├── realtimeVoice.py        # Reconnaissance vocale en temps réel
│   │   └── vosk-model-small-fr-0.22/  # Modèle de reconnaissance vocale français
│   ├── ressources/
│   │   ├── wizzard-test/          # Sprites de magiciens
│   │   └── tiles/                  # Cartes Tiled et tilesets
│   └── __pycache__/
│
├── server/                          # Code côté serveur
│   ├── main.py                     # Point d'entrée, gestion des clients et broadcast
│   ├── NetworkManager.py           # Gestion des connexions socket (singleton)
│   ├── gameState.py                # État global du jeu
│   ├── message.py                  # Protocole et types de messages
│   ├── collisions.py               # Détection des collisions côté serveur
│   ├── managers/
│   │   ├── entityManager.py        # Gestion des entités (joueurs, ennemis, etc.)
│   │   ├── collisionManager.py     # Gestion des collisions
│   │   └── iaManager.py            # Gestion de l'IA des ennemis
│   ├── ia/
│   │   └── pathFinding.py          # Algorithme de pathfinding
│   ├── classes/
│   │   └── serializable.py         # Classe de base sérialisable
│   └── __pycache__/
│
├── .github/                         # Configuration GitHub
├── README.md                       # Documentation du projet
├── CONTRIBUTING.md                 # Guide de contribution
├── CODE_IMPROVEMENTS.md            # Suggestions d'améliorations
├── requirements.txt                # Dépendances Python
└── .gitignore                      # Fichiers à ignorer
```

## 🔧 Architecture Technique

### Serveur

- **NetworkManager** : Gère les connexions socket TCP/IP en tant que singleton
- **GameState** : Maintient l'état global du jeu (joueurs, ennemis, entités)
- **Main.py** : Boucle serveur qui :
  - Accepte les connexions des clients
  - Traite les messages reçus (PLAYER_UPDATE, SPELL_CAST, etc.)
  - Gère les collisions côté serveur
  - Diffuse l'état du jeu à tous les clients toutes les 30ms (~30 FPS)
- **Managers** :
  - EntityManager : CRUD des entités
  - CollisionManager : Détection et résolution des collisions
  - IAManager : Gestion de l'IA des ennemis
- **Protocole** : Messages sérialisés avec pickle pour transport fiable

### Client

- **ClientManager** : Gère la connexion au serveur et reçoit les messages en thread séparé
- **GameManager** : Singleton qui gère :
  - L'initialisation de Pygame
  - La boucle de jeu (input → render → sync serveur)
  - Le rendu avec système de caméra suivi du joueur
  - Les animations des sprites
- **Player** : Représente un joueur avec :
  - Système d'animation (idle, walk, run, attack, hurt, dead)
  - Hitbox pour les collisions
  - Position et vélocité
  - État (vivant, mort, en cooldown, etc.)
- **UI** : Système custom avec :
  - Menus (main, host, join)
  - Positionnement anchor (top-left, center, etc.)
  - Gestion des événements
- **Voice** : Reconnaissance vocale en français avec Vosk

### Protocole de Communication

``` txt
Message = [Type (1 byte)][Data Length (4 bytes)][Data (pickle)]
```

**Types de messages :**

- `CONNECT` : Connexion initiale, envoie player_id
- `PLAYER_UPDATE` : Position du joueur (x, y)
- `GAME_STATE` : État complet du jeu (tous les joueurs, ennemis, etc.)
- `PLAYER_CAST_SPELL` : Lancement d'un sort
- `PLAYER_UPDATE_SPELL` : Mise à jour du cooldown d'un sort
- `DISCONNECT` : Déconnexion du joueur

**Fréquence :**

- Client → Serveur : À chaque changement (position, action)
- Serveur → Client : Broadcast 30 FPS (toutes les 33ms)

## 🤝 Contribuer

Nous accueillons les contributions ! Consultez [CONTRIBUTING.md](CONTRIBUTING.md) pour :

- Comment mettre en place votre environnement
- Les conventions de code à suivre
- Comment proposer des changements
- Les bonnes pratiques du projet

Lisez également [CODE_IMPROVEMENTS.md](CODE_IMPROVEMENTS.md) pour voir les améliorations actuellement priorisées.

## 🐛 Signaler un Bug

Si vous trouvez un bug, veuillez ouvrir une issue avec :

- Une description claire du problème
- Les étapes pour reproduire le bug
- Le comportement attendu vs le comportement actuel
- Votre configuration (OS, version Python, etc.)

## 📞 Contact

Pour toute question, n'hésitez pas à ouvrir une issue sur GitHub.

---

Bon jeu ! 🎮✨
