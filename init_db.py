import sqlite3

conn = sqlite3.connect('stadevisor.db')
cursor = conn.cursor()

# Table des utilisateurs
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'client'
''')

# Table des stades
cursor.execute('''
CREATE TABLE IF NOT EXISTS stadiums (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    location TEXT NOT NULL,
    capacity INTEGER NOT NULL
)
''')


# Création de la table reservations si elle n'existe pas
cursor.execute('''
CREATE TABLE IF NOT EXISTS reservations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stadium_id INTEGER,
    user_id INTEGER,
    date TEXT,
    time TEXT,
    FOREIGN KEY (stadium_id) REFERENCES stadiums(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
)
''')

conn.commit()
conn.close()
print("Base de données initialisée avec succès.")
