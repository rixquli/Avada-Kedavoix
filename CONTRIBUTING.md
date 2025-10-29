# Guide de Contribution - Avada-Kedavoix

Merci de votre intérêt pour contribuer à Avada-Kedavoix ! 🎮

## 🚀 Comment commencer

1. **Familiarisez-vous avec le projet**
   - Lisez le [README.md](README.md)
   - Exécutez le projet localement pour comprendre son fonctionnement
   - Explorez la structure du code

2. **Configurez votre environnement**
   ```bash
   git clone https://github.com/rixquli/Avada-Kedavoix.git
   cd Avada-Kedavoix
   pip install -r requirements.txt
   ```

## 📝 Types de contributions

### 🐛 Signaler des bugs

Utilisez les issues GitHub avec le template suivant :
- **Titre** : Description courte et claire du bug
- **Description** : Explication détaillée du problème
- **Étapes pour reproduire** : Comment reproduire le bug
- **Comportement attendu** : Ce qui devrait se passer
- **Comportement actuel** : Ce qui se passe réellement
- **Environnement** : OS, version Python, etc.

### ✨ Proposer de nouvelles fonctionnalités

Ouvrez une issue avec :
- Description de la fonctionnalité
- Cas d'usage
- Propositions d'implémentation (si applicable)

### 🔧 Contribuer au code

1. **Forkez et clonez**
   ```bash
   git clone https://github.com/votre-username/Avada-Kedavoix.git
   ```

2. **Créez une branche**
   ```bash
   git checkout -b feature/nom-de-votre-fonctionnalite
   ```

3. **Faites vos modifications**

4. **Testez vos changements**
   - Lancez le serveur et plusieurs clients
   - Vérifiez qu'il n'y a pas de régressions

5. **Committez**
   ```bash
   git add .
   git commit -m "feat: description claire de votre modification"
   ```

6. **Poussez et créez une Pull Request**
   ```bash
   git push origin feature/nom-de-votre-fonctionnalite
   ```

## 📐 Conventions de Code

### Style Python

Suivez les conventions PEP 8 :
- Indentation : 4 espaces
- Longueur de ligne : maximum 88 caractères (ou 120 si nécessaire)
- Noms de variables : `snake_case`
- Noms de classes : `PascalCase`
- Constantes : `UPPER_CASE`

### Structure du Code

```python
class ExempleClasse:
    """Description de la classe.
    
    Attributes:
        attribut1: Description de l'attribut
        attribut2: Description de l'attribut
    """
    
    def __init__(self, param1, param2):
        """Initialise la classe.
        
        Args:
            param1: Description du paramètre
            param2: Description du paramètre
        """
        self.attribut1 = param1
        self.attribut2 = param2
    
    def methode_exemple(self, param):
        """Description courte de la méthode.
        
        Args:
            param: Description du paramètre
            
        Returns:
            Description de ce qui est retourné
        """
        # Code ici
        pass
```

### Commentaires

- Ajoutez des docstrings pour toutes les classes et méthodes publiques
- Commentez les sections complexes du code
- Utilisez des commentaires en français ou en anglais (soyez cohérent)

### Messages de Commit

Format recommandé :
```
type: description courte

Description détaillée (optionnel)
```

Types :
- `feat`: Nouvelle fonctionnalité
- `fix`: Correction de bug
- `docs`: Documentation
- `style`: Formatage, missing semi colons, etc
- `refactor`: Refactorisation du code
- `test`: Ajout de tests
- `chore`: Maintenance, dépendances, etc

Exemples :
```
feat: ajout du système de sorts
fix: correction du bug de synchronisation des positions
docs: mise à jour du README avec les nouveaux contrôles
```

## 🏗️ Architecture du Projet

### Côté Serveur

- **`server/main.py`** : Point d'entrée, gère les connexions et le broadcast
- **`server/NetworkManager.py`** : Abstraction des sockets
- **`server/gameManager.py`** : État global du jeu
- **`server/managers/playersManager.py`** : CRUD des joueurs
- **`server/message.py`** : Protocole de communication

### Côté Client

- **`client/main.py`** : Boucle de jeu Pygame
- **`client/clientManager.py`** : Communication avec le serveur
- **`client/classes/player.py`** : Logique du joueur

### Ajouter une Nouvelle Fonctionnalité

1. **Définir le message** dans `server/message.py` si nécessaire
2. **Côté serveur** : Ajouter le traitement dans `server/main.py`
3. **Côté client** : Ajouter le traitement dans `client/clientManager.py`
4. **Tester** avec plusieurs clients

## 🧪 Tests

Actuellement, le projet n'a pas de suite de tests automatisés. C'est une excellente opportunité de contribution !

Pour tester manuellement :
1. Lancez le serveur
2. Lancez plusieurs clients (au moins 2-3)
3. Vérifiez que tous les joueurs se voient et se déplacent correctement
4. Testez les déconnexions/reconnexions

## 📋 Checklist avant Pull Request

- [ ] Mon code suit les conventions du projet
- [ ] J'ai testé mes changements localement
- [ ] J'ai ajouté des commentaires pour les parties complexes
- [ ] J'ai mis à jour la documentation si nécessaire
- [ ] Mes commits ont des messages clairs
- [ ] Mon code ne casse pas les fonctionnalités existantes

## 💡 Idées de Contributions

### Facile
- Améliorer les commentaires dans le code
- Ajouter des constantes pour les valeurs magiques (ports, vitesses, etc.)
- Améliorer les messages d'erreur

### Moyen
- Implémenter le système de sorts (base déjà présente)
- Ajouter des obstacles/collisions
- Système de score ou de points
- Améliorer les graphiques (sprites au lieu de cercles)

### Avancé
- Système de salles/lobbies
- Chat entre joueurs
- Base de données pour persistance
- Authentification des joueurs
- Tests unitaires et d'intégration

## 🤔 Besoin d'Aide ?

- Ouvrez une issue avec le tag `question`
- Consultez le code existant pour des exemples
- Regardez les Pull Requests déjà mergées

## 📜 Code de Conduite

- Soyez respectueux envers tous les contributeurs
- Acceptez les critiques constructives
- Focalisez-vous sur ce qui est le mieux pour le projet
- Faites preuve d'empathie envers les autres membres

---

Merci de contribuer à Avada-Kedavoix ! 🎉
