# Voting app

Project developed for Sorbonne Univerity 2nd year course in a group of 5 people from February 2024 to April 2024.

## About

Voting app allows to simulate election based on one or several voting rules.

### Features

- Several voting rules:
- Plurality 1 & 2 rounds
- - Borda
- - Veto
- - Condorcet, method Copeland & Simpson
- - Approval
- - Exhaustive ballot
- Graphs (tournament) for Condorcet-based voting rule
- Bar charts for one-round voting rules
- Stacked bar charts for multi round voting rules
- Tie-breaks:
- - Alphabetical
- - Duels based
- Liquid democracy
- Data generation based on Gaussian distribution
- Polls

## Requirements

- `python` >= 3.11
- `pip` (gestionnaire de paquets Python)

## Installation

Voting app uses framework _Qt_ for graphics as well as the library `numpy`. All requirements are listed in `requirements.txt`.

Here is a guide to install all dependencies

### Virtual environment

For better package management we recommend to create and activate a virtual environement before the installation of dependencies.

### Installation and use

1. Requirements installation

`pip install -r requirements.txt`

2. Run the app

`python3 main.py`

## Docs

Docs were generated with `pdoc`. It's located in `docs` folder.
