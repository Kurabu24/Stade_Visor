import sqlite3
from werkzeug.security import generate_password_hash

# Informations du compte admin
email = "admin@stadevisor.com"
password = "admin123"
hashed_pw = generate_password_hash(password)
role = "admin"

# Connexion à la base SQLite
conn = sqlite3.connect("stadevisor.db")
cursor = conn.cursor()

try:
    cursor.execute("INSERT INTO users (email, password_hash, role) VALUES (?, ?, ?)",
                (email, hashed_pw, role))
    conn.commit()
    print("✅ Compte admin créé avec succès.")
except sqlite3.IntegrityError:
    print("⚠️ Ce compte existe déjà.")
finally:
    conn.close()
