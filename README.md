Voici un exemple de fichier `README.md` pour ton projet **StadeVisor**, qui explique ce que fait le projet, comment l’installer et le lancer localement :

---

# 🏟️ StadeVisor

**StadeVisor** est une application web permettant de consulter la disponibilité des stades à Marseille et de réserver des créneaux horaires. Le site permet aux utilisateurs de s'inscrire, réserver des terrains, et aux entraîneurs ou administrateurs de gérer les créneaux.

## 🚀 Fonctionnalités principales

- ✅ Affichage des détails des stades
- 🗓️ Calendrier interactif avec créneaux horaires
- 📆 Réservation de créneaux (limite de 3h/semaine pour les clients)
- 🔒 Système d’authentification avec gestion des rôles (`client`, `trainer`, `admin`)
- 🧑 Les utilisateurs peuvent annuler leurs propres réservations

## 📁 Structure du projet

```
/stadvisor/
│
├── static/                  # Fichiers statiques (CSS, JS, images)
├── templates/               # Fichiers HTML (Jinja2)
│   ├── base.html
│   ├── index.html
│   ├── admin.html
│   ├── login.html
│   ├── register.html
│   ├── stadium_details.html
│   └── calendar.html
│
├── app.py                   # Application Flask principale
├── database.db              # Base de données SQLite
├── schema.sql               # Script SQL pour créer les tables
├── README.md                # Fichier d’explication du projet
└── requirements.txt         # Dépendances Python
```

## 🛠️ Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/ton-utilisateur/stadevisor.git
cd stadevisor
```

### 2. Créer un environnement virtuel

```bash
python -m venv venv
source venv/bin/activate   # Sur Windows : venv\Scripts\activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Créer la base de données

Si ce n’est pas déjà fait, initialise la base de données avec le fichier `schema.sql` :

```bash
sqlite3 database.db < schema.sql
```

Tu peux aussi créer un script Python d’initialisation si besoin.

### 5. Lancer le serveur Flask

```bash
flask run
```

Par défaut, l’application est accessible sur : [http://127.0.0.1:5000](http://127.0.0.1:5000)

## 🔑 Comptes par défaut (optionnel)

Tu peux insérer des utilisateurs ou stades de test manuellement dans la base avec `sqlite3` ou via un script Python d’initialisation.

## 📌 TODO et améliorations futures

- Ajouter une interface d'administration avancée
- Envoyer des mails de confirmation pour les réservations
- Ajouter la possibilité de filtrer les stades par localisation/type
- Interface mobile (responsive améliorée)

---