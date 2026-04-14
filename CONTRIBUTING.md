# Guide de Contribution - Avada-Kedavoix

Merci de votre intérêt pour contribuer à Avada-Kedavoix ! 🎮✨

## 🚀 Comment commencer

### Prérequis

- Git installé
- Python 3.10+
- Un éditeur de code (VS Code recommandé)
- Familiarité basique avec Python et Pygame

### Première Contribution

1. **Lisez la documentation**
   - [README.md](README.md) - Vue d'ensemble du projet
   - [CODE_IMPROVEMENTS.md](CODE_IMPROVEMENTS.md) - Améliorations en cours
   - Explorez la structure du code

2. **Configurez votre environnement**

   ```bash
   # Clonez le dépôt
   git clone https://github.com/rixquli/Avada-Kedavoix.git
   cd Avada-Kedavoix
   
   # Créez un environnement virtuel
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # source .venv/bin/activate  # Linux/Mac
   
   # Installez les dépendances
   pip install -r requirements.txt
   ```

3. **Testez l'installation**

   ```bash
   # Terminal 1 : démarrer le serveur
   python server/main.py
   
   # Terminal 2 : démarrer le client
   python client/main.py
   ```

## 📝 Types de contributions

### 🐛 Signaler des bugs

Utilisez les issues GitHub avec le template suivant :

- **Titre** : Description courte et claire du bug
- **Description** : Explication détaillée du problème
- **Étapes pour reproduire** : Comment reproduire le bug
- **Comportement attendu** : Ce qui devrait se passer
- **Comportement actuel** : Ce qui se passe réellement
- **Environnement** :
  - OS (Windows, Linux, Mac)
  - Version Python (`python --version`)
  - Traces d'erreur complètes
  - Logs du serveur/client

**Exemple :**

```txt
Title: Joueur se téléporte après déconnexion/reconnexion

Description: 
Quand un joueur se reconnecte, sa position ne se synchronise pas correctement
et il apparaît à une position aléatoire.

Steps to reproduce:
1. Lancer le serveur
2. Connecter un client
3. Se déplacer et fermer le client
4. Reconnecter le même client
5. Observer la position du joueur

Expected: Position correcte (où le joueur était avant)
Actual: Position aléatoire
```

### ✨ Proposer de nouvelles fonctionnalités

Ouvrez une issue avec :

- Description claire de la fonctionnalité
- Cas d'usage / bénéfices
- Propositions d'implémentation (API, architecture)
- Mockups ou exemples si applicable
- Impact sur les performances

**Exemple :**

```txt
Title: Ajouter un système de cooldown visuel pour les sorts

Description:
Les joueurs ne savent pas quand leurs sorts seront à nouveau disponibles.
Une barre de cooldown afficherait le temps d'attente.

Implementation ideas:
- Afficher une barre au-dessus du joueur
- Couleur : rouge (pas disponible) → vert (disponible)
- Animation lisse avec PyGame
```

### 🔧 Contribuer au code

#### Workflow

1. **Forkez et clonez**

   ```bash
   # Forkez sur GitHub (bouton Fork)
   git clone https://github.com/VOTRE-USERNAME/Avada-Kedavoix.git
   cd Avada-Kedavoix
   ```

2. **Créez une branche descriptive**

   ```bash
   # Pour une correction de bug
   git checkout -b fix/nom-descriptif-du-bug
   
   # Pour une nouvelle fonctionnalité
   git checkout -b feature/nom-de-la-fonctionnalite
   
   # Pour une amélioration
   git checkout -b improve/nom-de-lamelioration
   ```

3. **Faites vos modifications**
   - Respectez les conventions du projet
   - Écrivez du code lisible et commenté
   - Testez vos changements
   - Ne modifiez que ce qui est nécessaire

4. **Testez vos changements**

   ```bash
   # Terminal 1
   python server/main.py
   
   # Terminal 2, 3, 4... (tester avec plusieurs clients)
   python client/main.py
   
   # Vérifiez que :
   # - Le serveur démarre sans erreur
   # - Les clients se connectent correctement
   # - Les mouvements sont synchronisés
   # - Les déconnexions sont gracieuses
   # - Aucune régression des fonctionnalités existantes
   ```

5. **Committez avec messages clairs**

   ```bash
   git add .
   git commit -m "type: description courte

   Description détaillée (optionnel)
   - Point 1
   - Point 2"
   ```

6. **Poussez et créez une Pull Request**

   ```bash
   git push origin feature/nom-de-votre-fonctionnalite
   ```

   Puis ouvrez une PR sur GitHub

#### Exemple de contribution complète

Disons que vous voulez ajouter un système de santé pour les joueurs :

```bash
# 1. Créer la branche
git checkout -b feature/player-health-system

# 2. Modifier les fichiers
# - client/classes/player.py : ajouter hp, max_hp
# - server/gameState.py : synchroniser les HP
# - client/gameManager.py : afficher la barre de santé

# 3. Tester
python server/main.py
python client/main.py  # Tester que ça marche

# 4. Commit
git add .
git commit -m "feat: add player health system

- Add hp and max_hp to Player class
- Display health bar above player
- Sync health with server
- Damage player on spell hit"

# 5. Push et PR
git push origin feature/player-health-system
# Créer PR sur GitHub
```

## 📐 Conventions de Code

### Style Python (PEP 8)

**Indentation et longueur :**

```python
# ✅ BON
def calculate_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """Calcule la distance entre deux points.
    
    Args:
        x1: Coordonnée X du point 1
        y1: Coordonnée Y du point 1
        x2: Coordonnée X du point 2
        y2: Coordonnée Y du point 2
        
    Returns:
        La distance euclidienne entre les deux points
    """
    dx = x2 - x1
    dy = y2 - y1
    return (dx ** 2 + dy ** 2) ** 0.5

# ❌ MAUVAIS
def calc_dist(x1, y1, x2, y2):
    # calcule distance
    return ((x2-x1)**2+(y2-y1)**2)**0.5
```

**Nommage :**

```python
# ✅ BON
class PlayerAnimator:
    def __init__(self):
        self.current_frame = 0
        self.animation_speed = 0.1
    
    def update_animation(self, delta_time: float) -> None:
        self.current_frame += delta_time * self.animation_speed

# ❌ MAUVAIS
class plyrAnimator:
    def __init__(self):
        self.cf = 0
        self.as = 0.1
    
    def updateAnimation(self, dt):
        self.cf += dt * self.as
```

**Imports :**

```python
# ✅ BON - Imprts organisés
import os
import sys
from typing import Dict, List, Optional
import pygame
from client.classes.player import Player
from server.message import Message

# ❌ MAUVAIS
import pygame; import os
from client.classes.player import Player; from server.message import Message
```

### Docstrings et Commentaires

**Format docstring :**

```python
class Player:
    """Représente un joueur dans le jeu.
    
    Un joueur peut se déplacer, lancer des sorts et prendre des dégâts.
    
    Attributes:
        x: Position X du joueur
        y: Position Y du joueur
        hp: Points de vie actuels
        max_hp: Points de vie maximum
        velocity_x: Vélocité sur l'axe X
        velocity_y: Vélocité sur l'axe Y
    """
    
    def __init__(self, x: float, y: float, hp: int = 100):
        """Initialise un joueur.
        
        Args:
            x: Position X initiale
            y: Position Y initiale
            hp: Points de vie initiaux (défaut: 100)
        """
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = hp
    
    def take_damage(self, amount: int) -> bool:
        """Inflige des dégâts au joueur.
        
        Args:
            amount: Montant des dégâts à infliger
            
        Returns:
            True si le joueur est mort, False sinon
        """
        self.hp -= amount
        return self.hp <= 0
```

**Commentaires pour le code complexe :**

```python
# ✅ BON - Explique le POURQUOI, pas le QUOI
def resolve_collision(entity1, entity2):
    # Les joueurs ne peuvent pas passer à travers les murs
    # On utilise SAT (Separating Axis Theorem) pour détecter/résoudre les collisions
    overlap = calculate_overlap(entity1.hitbox, entity2.hitbox)
    if overlap:
        push_entity_out(entity1, entity2, overlap)

# ❌ MAUVAIS - Redondant et inutile
def resolve_collision(entity1, entity2):
    # Calculer l'overlap
    overlap = calculate_overlap(entity1.hitbox, entity2.hitbox)
    # Vérifier si overlap
    if overlap:
        # Pousser l'entité
        push_entity_out(entity1, entity2, overlap)
```

### Type Hints

```python
from typing import Dict, List, Optional, Tuple

# ✅ BON
def get_player_by_id(player_id: int) -> Optional[Player]:
    """Retourne le joueur avec l'ID spécifié, ou None."""
    return self.players.get(player_id)

def broadcast_game_state(clients: List[socket.socket], state: Dict) -> None:
    """Envoie l'état du jeu à tous les clients."""
    for client in clients:
        send_message(client, state)

def calculate_spawn_position() -> Tuple[float, float]:
    """Retourne une position de spawn (x, y)."""
    return (random.randint(0, 1280), random.randint(0, 720))

# ❌ MAUVAIS
def get_player_by_id(player_id):
    return self.players.get(player_id)

def broadcast_game_state(clients, state):
    for client in clients:
        send_message(client, state)
```

### Organisation des fichiers

- **Imports** : En haut du fichier, organisés (stdlib, 3e partie, local)
- **Docstring du module** : Au très début
- **Constantes** : Après les imports
- **Classes** : Avant les fonctions
- **Code principal** : À la fin (dans `if __name__ == "__main__"`)

```python
"""
Module pour gérer l'état du jeu serveur.

Contient les classes pour représenter l'état global du jeu
et les entités (joueurs, ennemis, etc.)
"""

import time
from typing import Dict, List
import pygame
from client.classes.player import Player
from server.message import Message

# Constantes
DEFAULT_SPAWN_X = 640
DEFAULT_SPAWN_Y = 360
MAX_PLAYERS = 10

class GameState:
    """Représente l'état global du jeu."""
    
    def __init__(self):
        self.players: Dict[int, Player] = {}
        self.entities: List = []
    
    def add_player(self, player: Player) -> int:
        """Ajoute un joueur et retourne son ID."""
        player_id = len(self.players)
        self.players[player_id] = player
        return player_id

def main():
    """Fonction principale."""
    pass

if __name__ == "__main__":
    main()
```

## 🏗️ Architecture du Projet

### Où ajouter du code ?

**Client-side features :**

- Interface/menus → `client/ui/`
- Logique de personnage → `client/classes/player.py`
- Gestion réseau côté client → `client/clientManager.py`
- Boucle de jeu → `client/gameManager.py`

**Server-side features :**

- Logique de jeu → `server/main.py`
- Gestion des entités → `server/managers/entityManager.py`
- IA/pathfinding → `server/ia/`
- Collisions → `server/managers/collisionManager.py`

**Messages/Protocole :**

- Nouveaux types de messages → `server/message.py`
- Types partagés → `server/message.py`

### Ajouter une Nouvelle Fonctionnalité

**Exemple : Ajouter un système de cooldown de sort**

1. **Côté serveur** (`server/message.py`) :

   ```python
   class SpellCooldownData(TypedDict):
       spell_id: int
       cooldown_remaining: float
   ```

2. **Côté serveur** (`server/main.py`) :

   ```python
   # Traiter le message de sort
   match msg_t["type"]:
       case MessageType.PLAYER_CAST_SPELL:
           spell_id = msg.data["spell_id"]
           # Vérifier le cooldown
           if player.can_cast_spell(spell_id):
               # Créer le sort, le lancer, etc.
               pass
   ```

3. **Côté client** (`client/gameManager.py`) :

   ```python
   # Recevoir les mises à jour de cooldown
   def handle_spell_cooldown(self, cooldown_data):
       self.player.spells[cooldown_data["spell_id"]].cooldown = \
           cooldown_data["cooldown_remaining"]
   ```

4. **Côté client** (`client/classes/player.py`) :

   ```python
   # Afficher le cooldown
   def draw_spell_cooldown(self, surface):
       if self.current_spell_cooldown > 0:
           # Dessiner une barre
           pass
   ```

5. **Testez** :

   ```bash
   python server/main.py
   python client/main.py
   # Lancer un sort et observer le cooldown
   ```

## 🧪 Tests

### Tester manuellement

```bash
# Terminal 1 : Serveur
python server/main.py

# Terminals 2+ : Clients
python client/main.py
```

Vérifiez :

- ✅ Connexion/déconnexion
- ✅ Mouvements synchronisés entre clients
- ✅ Pas d'erreurs dans les logs
- ✅ Pas de ralentissements
- ✅ Pas de déconnexions inattendues
- ✅ Votre nouvelle feature fonctionne

### Tests automatisés (futurs)

```bash
# Une fois les tests mis en place
pytest tests/
```

## 📋 Checklist avant Pull Request

- [ ] Votre code suit les conventions PEP 8
- [ ] Tous les docstrings sont présents
- [ ] Type hints sur les APIs publiques
- [ ] Pas de `print()` (utiliser logging si nécessaire)
- [ ] Tests manuels effectués (aucune régression)
- [ ] Commits avec messages clairs
- [ ] Branche à jour avec `main`
- [ ] Description de PR claire
- [ ] Screenshots/GIFs si relevant
- [ ] Pas de code "mort" ou temporaire

**Template de PR :**

```markdown
## Description
Brève description de ce que cette PR fait

## Type de changement
- [x] Bug fix (correction qui ne casse pas les tests existants)
- [ ] Nouvelle fonctionnalité
- [ ] Breaking change (correction/feature qui change le comportement existant)

## Comment tester
Étapes pour tester le changement :
1. Lancer le serveur
2. Lancer un client
3. ...

## Checklist
- [x] Mon code suit les conventions du projet
- [x] J'ai testé manuellement
- [x] Pas de régressions
```

## 💡 Idées de Contributions (Classées par Difficulté)

### ⭐ Facile

- Améliorer les commentaires/docstrings
- Ajouter des constantes pour les valeurs "magiques"
- Améliorer les messages d'erreur
- Corriger les typos
- Améliorer la documentation

### ⭐⭐ Moyen

- Implémenter le système de sorts (base existe déjà)
- Ajouter des obstacles/collisions
- Système de score ou de points
- Améliorer les graphiques (sprites au lieu de cercles)
- Ajouter des effets sonores
- Système de santé pour les joueurs

### ⭐⭐⭐ Avancé

- Système de salles/lobbies
- Chat entre joueurs
- Base de données pour persistance
- Authentification des joueurs
- Tests unitaires et d'intégration
- Refactor pour améliorer la performance
- Système d'équipement/items

## 🤔 Besoin d'Aide ?

- **Questions sur le code ?** Ouvrez une issue avec le tag `question`
- **Consultez le code existant** pour trouver des exemples
- **Regardez les PRs mergeées** pour voir comment c'est fait
- **Contactez l'équipe** si vous êtes bloqué

## 📜 Code de Conduite

- Soyez respectueux envers tous les contributeurs
- Acceptez les critiques constructives
- Focalisez-vous sur ce qui est le mieux pour le projet
- Faites preuve d'empathie envers les autres membres
- Pas de spam, harcèlement ou contenu offensant

## 🎯 À Retenir

1. **Code propre** : Lisible et maintenable
2. **Documentation** : Docstrings + commentaires pour le complexe
3. **Tests** : Vérifiez que ça marche et que c'est pas cassé
4. **Commits clairs** : Messages explicites
5. **Petites PRs** : Plus facile à review

---

Merci encore de contribuer à Avada-Kedavoix ! 🎉
