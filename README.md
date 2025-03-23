# StadeVisor

StadeVisor est une application web permettant d'afficher les disponibilités des stades à Marseille et de réserver des heures pour jouer librement.

## Prérequis

Avant d'installer le projet, assurez-vous d'avoir les éléments suivants installés sur votre machine :

- [Node.js](https://nodejs.org/) (version 16 ou supérieure recommandée)
- [npm](https://www.npmjs.com/) (installé avec Node.js)
- [Git](https://git-scm.com/)

## Installation

1. Clonez ce dépôt :

   ```bash
   git clone https://github.com/votre-utilisateur/StadeVisor.git
   cd StadeVisor
   ```

2. Installez les dépendances :

   ```bash
   npm install
   ```

3. Configurez la base de données SQLite :

   ```bash
   npm run migrate
   ```

## Démarrage du serveur

Pour démarrer l'application en mode développement, exécutez :

```bash
npm start
```

Le serveur sera accessible sur : `http://localhost:3000`

## Structure du projet

```
StadeVisor/
├── controllers/      # Logique des routes
├── models/           # Gestion de la base de données
├── routes/           # Définition des routes Express
├── views/            # Fichiers Mustache pour l'affichage
├── public/           # Fichiers statiques (CSS, JS)
├── app.js            # Point d'entrée principal
├── package.json      # Fichier de configuration npm
└── README.md         # Documentation du projet
```

## Technologies utilisées

- **Node.js** + **Express.js** : Backend
- **Mustache** : Templates HTML
- **SQLite** : Base de données
- **Tailwind CSS** : Stylisation de l'interface utilisateur

## Fonctionnalités

- Affichage des stades et de leurs disponibilités
- Formulaire de réservation d'un créneau
- Interface responsive avec Tailwind CSS
- Gestion des utilisateurs avec authentification

## Contributions

Les contributions sont les bienvenues ! Merci de forker le dépôt et de proposer une pull request.

## Licence

Ce projet est sous licence MIT.

## Auteurs

📧 Contact : <akram.bouhraoua@etu.univ-amu.fr> - <martin.pouget@etu.univ-amu.fr>
🌐 Site officiel : (en cours de developpement )
