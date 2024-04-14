# Application de vote. Groupe _tzb_

## Participants

- Ekaterina Bogush 21214957
- Pâris Tran
- Rehyann Bouteiller 21100713
- Haroun Zerdoumi 21212992
- Hadrien de La Taille Lolainville 21103191

## À propos

Notre application de vote permet de simuler une élection selon les différentes règles de vote ou d'effectuer les sondages.

### Features

- Plusieurs règles de vote disponible:
- - Pluralité à un et à deux tours
- - Borda
- - Veto
- - Condorcet avec les méthodes de Copeland et de Simpson
- - Vote par approbation
- - Eliminations successives
- Affichage des résultats avec des diagrammes et des graphes
- Résolution des égalités entre les candidats selon les duels
- Démocratie liquide
- Génération des données selon la loi normale
- Sondages

## Prérequis

Avant de commencer, assurez-vous d'avoir installé le logiciel suivant:

- `python` >= 3.11
- `pip` (gestionnaire de paquets Python)

## Installation

Notre application utilise le framework _Qt_, ainsi que la bibliothéque `numpy`. La liste complète des dépendences se trouve dans `requirement.txt`.

Pour installer les dépendences requises suivez les étapes:

### MacOS, Linux

1. Création de l'environnement virtuel

`python3 -m venv <chemin/vers/environnement/>`.

Un chemin doit contenir le nom l'environnement virtuel.

2. Activer l'environnement virtuel

`source <chemin/vers/environnement/>/bin/activate`

Si l'environnement a été bien activé, son nom entre les parathèses doit appraître au début de la ligne des commandes.

3. Cloner le répo

- Naviguer dans le répertoire où vous voulez stocker une application de vote.
- Cloner le répo `git clone <lien_vers_répo>`

Il est possible de passer par le protocol SSH ou HTTPS.

3. Installer les prérequis selon `requirement.txt`

`pip install -r requirements.txt`

4. Lancer une application

`python3 main.py`

### Windows

#### Installation de git

1. Aller sur [le site de Git](http://msysgit.github.io/) et télécharger le fichier `.exe` pour Windows

2. Lancer ce fichier téléchargé

#### Installation et utilisation de l'environnement virtuel

1. Installation de l'environnement virtuel

`pip install virtualenv`

2. Création de l'environnement virtuel dans le répertoire courant

`virtualenv myenv`

3. Modifier les accès aux exécutions de windows (le rétablir normalement avec `Set-ExecutionPolicy Restricted` après utilisation)

- Lancer Windows powershell en administrateur
- Utiliser `Set-ExecutionPolicy RemoteSigned`

4. Modifier le _PATH_ du système dans les paramètres

- Entrer dans _modifier les variables d'environnement système_ dans la recherche sur la touche Windows
- Entrer dans _Variables d'environnement_
- Cliquer sur _path_ dans _variables système_
- Cliquer sur nouveau
- Entrer le path recommendé par le système afin de pouvoir activer
  `C:\Users\...\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\Scripts`

**_Attention_**: ce path est différent pour chaque pc et utilisateur, celui présenté est un exemple

5. Activer l'environnement virtuel

- Entrer dans le fichier `\Scripts` du répertoire de l'environnement virtuel
- `.\activate.bat`

Si l'environnement a été bien activé, son nom entre les parathèses doit appraître au début de la ligne des commandes.

6. Cloner le répo

- Naviguer dans le répertoire où vous voulez stocker une application de vote.
- Cloner le répo `git clone <lien_vers_répo>`

Il est possible de passer par le protocol SSH ou HTTPS.

7. Installer les prérequis selon `requirement.txt`

`pip install -r requirements.txt`

8. Lancer une application

`python3 main.py`

## Utilisation (tutoriels)
