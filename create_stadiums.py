import sqlite3

# Connexion à la base de données
conn = sqlite3.connect('stadevisor.db')

# Créer des stades
stades = [
    ('Stade de Marseille', 'Marseille, France', 5000),
    ('Stade Pierre-Mauroy', 'Lille, France', 25000),
    ('Stade de France', 'Saint-Denis, France', 80000)
]

# Insérer les stades dans la base de données
conn.executemany('''
    INSERT INTO stadiums (name, location, capacity) VALUES (?, ?, ?)
''', stades)

conn.commit()
conn.close()

print("3 stades ont été créés.")
