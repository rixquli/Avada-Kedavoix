# Avada-Kedavoix 🎮

## 📝 Description

Avada-Kedavoix est un jeu multijoueur en temps réel développé en Python avec Pygame. Les joueurs peuvent se déplacer dans un environnement 2D et interagir avec d'autres joueurs en réseau via une architecture client-serveur.

## ✨ Fonctionnalités

- 🎮 Jeu multijoueur en temps réel
- 🌐 Architecture client-serveur avec sockets
- 🎨 Interface graphique avec Pygame
- 👥 Support de plusieurs joueurs simultanés
- 🎯 Système de mouvements fluides (ZQSD ou flèches directionnelles)
- 🔄 Synchronisation automatique de l'état du jeu entre clients

## 📋 Prérequis

- Python 3.10 ou supérieur
- pygame
- watchdog (optionnel, pour le rechargement automatique du serveur)

## 🚀 Installation

1. **Clonez le dépôt** :
   ```bash
   git clone https://github.com/rixquli/Avada-Kedavoix.git
   cd Avada-Kedavoix
   ```

2. **Installez les dépendances** :
   ```bash
   pip install pygame watchdog
   ```

## 🎯 Utilisation

### Démarrer le serveur

Dans un premier terminal, lancez le serveur :

```bash
python server\main.py
```

Ou avec rechargement automatique lors de modifications du code :

```bash
watchmedo auto-restart --patterns="*.py" --recursive -- python server\main.py
```

Le serveur démarrera par défaut sur `localhost:12345`.

### Démarrer un ou plusieurs clients

Dans un autre terminal (ou plusieurs pour simuler plusieurs joueurs), lancez le client :

```bash
python client\main.py
```

Chaque client se connectera automatiquement au serveur et apparaîtra avec une couleur différente.

### Contrôles

- **Déplacement** : Utilisez les flèches directionnelles ou ZQSD
  - ⬆️ Haut : `Z` ou `Flèche Haut`
  - ⬇️ Bas : `S` ou `Flèche Bas`
  - ⬅️ Gauche : `Q` ou `Flèche Gauche`
  - ➡️ Droite : `D` ou `Flèche Droite`

## 🏗️ Architecture du Projet

```
avada-kedavoix/
├── client/                      # Code côté client
│   ├── main.py                 # Point d'entrée du client
│   ├── clientManager.py        # Gestion de la connexion et des messages
│   └── classes/
│       └── player.py           # Classe représentant un joueur
│
├── server/                      # Code côté serveur
│   ├── main.py                 # Point d'entrée du serveur
│   ├── NetworkManager.py       # Gestion des connexions réseau
│   ├── gameManager.py          # Gestion de l'état du jeu
│   ├── message.py              # Définition des types de messages
│   └── managers/
│       └── playersManager.py   # Gestion des joueurs côté serveur
│
└── README.md                    # Ce fichier
```

## 🔧 Architecture Technique

### Serveur

- **NetworkManager** : Gère les connexions socket et la communication réseau
- **GameManager** : Maintient l'état global du jeu
- **PlayersManager** : Gère l'ajout, la suppression et la mise à jour des joueurs
- **Broadcasting** : Diffuse l'état du jeu à tous les clients 30 fois par seconde

### Client

- **ClientManager** : Gère la connexion au serveur et la réception des messages
- **Player** : Représente un joueur avec sa position, couleur, et mouvements
- **Boucle de jeu Pygame** : Affiche les graphiques à 60 FPS

### Protocole de Communication

Le projet utilise un système de messages sérialisés avec les types suivants :
- `CONNECT` : Connexion initiale d'un joueur
- `PLAYER_UPDATE` : Mise à jour de la position d'un joueur
- `GAME_STATE` : État complet du jeu (broadcast du serveur)
- `PLAYER_CAST_SPELL` : Lancement d'un sort (fonctionnalité future)

## 🤝 Contribuer

Nous accueillons les contributions ! Voici comment participer :

1. **Forkez le projet**
2. **Créez une branche pour votre fonctionnalité** :
   ```bash
   git checkout -b feature/ma-nouvelle-fonctionnalite
   ```
3. **Committez vos changements** :
   ```bash
   git commit -m "Ajout d'une nouvelle fonctionnalité"
   ```
4. **Poussez vers la branche** :
   ```bash
   git push origin feature/ma-nouvelle-fonctionnalite
   ```
5. **Ouvrez une Pull Request**

### Conventions de Code

- Utilisez des noms de variables et fonctions en anglais ou français (cohérence)
- Ajoutez des docstrings pour les classes et méthodes
- Suivez les conventions PEP 8 pour Python
- Commentez les sections complexes du code

### Idées de Contributions

- 🎨 Améliorer les graphiques (sprites, animations)
- 🔮 Implémenter le système de sorts
- 🏆 Ajouter un système de score
- 🗺️ Créer une carte de jeu avec obstacles
- 🔊 Ajouter des effets sonores
- 🛡️ Améliorer la sécurité réseau
- 📊 Ajouter des statistiques de jeu

## 🐛 Signaler un Bug

Si vous trouvez un bug, veuillez ouvrir une issue avec :
- Une description claire du problème
- Les étapes pour reproduire le bug
- Le comportement attendu vs le comportement actuel
- Votre configuration (OS, version Python, etc.)

## 📜 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 👥 Auteurs

- **Théo** - Développeur principal
- Contributeurs : Voir la liste des [contributeurs](https://github.com/rixquli/Avada-Kedavoix/contributors)

## 📞 Contact

Pour toute question, n'hésitez pas à ouvrir une issue sur GitHub.

---

Bon jeu ! 🎮✨