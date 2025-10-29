# 🎮 Client - Avada-Kedavoix

Ce dossier contient tout le code côté client du jeu.

## 📁 Structure

- **`main.py`** : Point d'entrée du client. Lance la boucle de jeu Pygame.
- **`clientManager.py`** : Gère la connexion au serveur et la réception des messages.
- **`classes/`** : Contient les classes du client
  - **`player.py`** : Classe représentant un joueur (position, mouvements, affichage)

## 🔧 Fonctionnement

### Boucle Principale (`main.py`)

1. Initialise Pygame et crée la fenêtre
2. Se connecte au serveur via `ClientManager`
3. Boucle de jeu (60 FPS) :
   - Gère les événements (fermeture, touches)
   - Met à jour la position du joueur local
   - Dessine tous les joueurs
   - Envoie la position au serveur

### Gestion Réseau (`clientManager.py`)

- **Thread de réception** : Écoute en permanence les messages du serveur
- **Synchronisation** : Met à jour l'état local à partir des données serveur
- **Envoi** : Transmet la position du joueur local au serveur

### Classe Player (`classes/player.py`)

Représente un joueur avec :
- Position (x, y)
- Vélocité (vx, vy)
- Apparence (color, radius)
- Méthodes :
  - `update()` : Met à jour la position
  - `handle_input()` : Gère les touches clavier
  - `draw()` : Dessine le joueur sur l'écran

## 🚀 Lancement

```bash
python client\main.py
```

Le client se connectera automatiquement à `localhost:12345`.

## 🎯 Améliorations Futures

- [ ] Ajouter des animations
- [ ] Implémenter le système de sorts
- [ ] Améliorer les graphiques (sprites)
- [ ] Ajouter des effets sonores
- [ ] Interface utilisateur (score, vie, etc.)
