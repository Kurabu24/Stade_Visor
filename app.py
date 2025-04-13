# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash,jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
app.secret_key = 'secret-key'
DATABASE = 'stadevisor.db'

def get_db_connection():
    conn = sqlite3.connect('stadevisor.db')
    conn.row_factory = sqlite3.Row  # Permet de récupérer les résultats sous forme de dictionnaires
    return conn

@app.route('/toggle-dark-mode', methods=['POST'])
def toggle_dark_mode():
    current = session.get('dark_mode', False)
    session['dark_mode'] = not current
    return jsonify({'dark_mode': session['dark_mode']})


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn
def get_week_range(date_str):
    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    start_of_week = date_obj - timedelta(days=date_obj.weekday())  # lundi
    end_of_week = start_of_week + timedelta(days=6)  # dimanche
    return start_of_week, end_of_week

@app.route("/admin/stadium/create", methods=["GET", "POST"])
def create_stadium():
    if request.method == "POST":
        name = request.form["name"]
        location = request.form["location"]
        capacity = request.form["capacity"]
        
        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO stadiums (name, location, capacity) VALUES (?, ?, ?)",
                        (name, location, capacity))
            conn.commit()
            flash("Stade créé avec succès.")
            return redirect("/admin/stadium/create")
        except Exception as e:
            flash(f"Erreur : {e}")
        finally:
            conn.close()

    return render_template("admin.html")


# Auth routes
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

        if user and check_password_hash(user["password_hash"], password):  # Assure-toi de vérifier le mot de passe de manière sécurisée
            session["user_id"] = user["id"]  # Stocker l'ID de l'utilisateur dans la session
            flash("Connexion réussie")
            if user["role"] == "admin":
                return redirect(url_for("admin_dashboard"))
            return redirect(url_for("index"))
        else:
            flash("Identifiants incorrects")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")  # Utilise .get() pour éviter l'IndexError
        password = request.form.get("password")
        password_confirm = request.form.get("password_confirm")

        # Vérification des champs
        if not email or not password or not password_confirm:
            flash("Tous les champs sont requis")
            return redirect(url_for("register"))

        # Vérification si les mots de passe correspondent
        if password != password_confirm:
            flash("Les mots de passe ne correspondent pas")
            return redirect(url_for("register"))

        # Vérification si l'email existe déjà
        conn = get_db_connection()
        existing_user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

        if existing_user:
            flash("Cet email est déjà utilisé")
            return redirect(url_for("register"))

        # Hachage du mot de passe (utilisation de werkzeug)
        hashed_password = generate_password_hash(password)

        # Enregistrement du nouvel utilisateur (par défaut rôle "client")
        conn.execute("INSERT INTO users (email, password_hash, role) VALUES (?, ?, ?)",
                    (email, hashed_password, "client"))
        conn.commit()
        conn.close()

        flash("Compte créé avec succès. Vous pouvez maintenant vous connecter.")
        return redirect(url_for("login"))

    return render_template("register.html")




@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route("/")
def index():
    user_id = session.get("user_id")
    role = None
    stadiums = []
    conn = get_db_connection()
    stadiums = conn.execute("SELECT * FROM stadiums").fetchall()

    if user_id:
        
        user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if user:
            role = user["role"]
    conn.close()

    return render_template("index.html", role=role, stadiums=stadiums)

@app.route('/admin/reservations/delete/<int:reservation_id>', methods=['POST'])
def delete_reservation(reservation_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM reservations WHERE id = ?', (reservation_id,))
    conn.commit()
    flash("Réservation supprimée.")
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/users/change_role/<int:user_id>', methods=['POST'])
def change_user_role(user_id):
    new_role = request.form['role']
    conn = get_db_connection()
    conn.execute('UPDATE users SET role = ? WHERE id = ?', (new_role, user_id))
    conn.commit()
    flash(f"Rôle de l'utilisateur {user_id} modifié en {new_role}.")
    return redirect(url_for('admin_dashboard'))



@app.route("/cancel_reservation", methods=["POST"])
def cancel_reservation():
    user_id = session.get("user_id")

    if not user_id:
        flash("Vous devez être connecté pour annuler une réservation.")
        return redirect(url_for("login"))

    reservation_id = request.form["reservation_id"]
    stadium_id = request.form["stadium_id"]

    # Connexion à la base de données
    conn = get_db_connection()

    # Récupérer la réservation à annuler
    reservation = conn.execute(
        "SELECT * FROM reservations WHERE id = ? AND user_id = ?",
        (reservation_id, user_id)
    ).fetchone()

    if reservation:
        # Annuler la réservation
        conn.execute(
            "DELETE FROM reservations WHERE id = ?",
            (reservation_id,)
        )
        conn.commit()
        flash("Réservation annulée avec succès.")
    else:
        flash("Aucune réservation trouvée pour ce créneau ou vous ne pouvez pas annuler cette réservation.")

    conn.close()

    return redirect(url_for("stadium_details", stadium_id=stadium_id))
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get("user_id")
        if not user_id:
            return redirect(url_for("login"))

        conn = get_db_connection()
        user = conn.execute("SELECT role FROM users WHERE id = ?", (user_id,)).fetchone()
        conn.close()

        if not user or user["role"] != "admin":
            flash("Accès réservé à l'administrateur.")
            return redirect(url_for("index"))

        return f(*args, **kwargs)
    return decorated_function

@app.route("/admin")
@admin_required
def admin_dashboard():
    conn = get_db_connection()
    users = conn.execute("SELECT * FROM users").fetchall()
    stadiums = conn.execute("SELECT * FROM stadiums").fetchall()
    reservations = conn.execute("SELECT * FROM reservations").fetchall()
    conn.close()
    return render_template("admin_dashboard.html", users=users, stadiums=stadiums, reservations=reservations)

@app.route("/admin/delete_all_reservations", methods=["POST"])
@admin_required
def delete_all_reservations():
    conn = get_db_connection()
    conn.execute("DELETE FROM reservations")
    conn.commit()
    conn.close()
    flash("Toutes les réservations ont été supprimées.")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/add_stadium", methods=["POST"])
@admin_required
def add_stadium():
    name = request.form["name"]
    location = request.form["location"]
    capacity = request.form["capacity"]

    conn = get_db_connection()
    conn.execute("INSERT INTO stadiums (name, location, capacity) VALUES (?, ?, ?)",
                (name, location, capacity))
    conn.commit()
    conn.close()
    flash("Stade ajouté avec succès.")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/delete_stadium/<int:stadium_id>", methods=["POST"])
@admin_required
def delete_stadium(stadium_id):
    conn = get_db_connection()

    # Supprimer les réservations liées à ce stade
    conn.execute("DELETE FROM reservations WHERE stadium_id = ?", (stadium_id,))

    # Ensuite supprimer le stade
    conn.execute("DELETE FROM stadiums WHERE id = ?", (stadium_id,))

    conn.commit()
    conn.close()

    flash("Stade et ses réservations associées supprimés.", category='success')
    return redirect(url_for("admin_dashboard"))




@app.route("/stadium/<int:stadium_id>", methods=["GET", "POST"])
def stadium_details(stadium_id):
    user_id = session.get("user_id")

    if not user_id:
        flash("Vous devez être connecté pour réserver un créneau.")
        return redirect(url_for("login"))

    conn = get_db_connection()
    stadium = conn.execute("SELECT * FROM stadiums WHERE id = ?", (stadium_id,)).fetchone()

    if stadium is None:
        flash("Le stade n'existe pas.")
        return redirect("/")

    if request.method == "POST":
        reservation_date = request.form["date"]
        reservation_time = request.form["time"]

        user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        role = user["role"]

        def get_week_range(date_str):
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            start_of_week = date_obj - timedelta(days=date_obj.weekday())  # lundi
            end_of_week = start_of_week + timedelta(days=6)  # dimanche
            return start_of_week, end_of_week

        start_week, end_week = get_week_range(reservation_date)

        # Vérification des réservations de la semaine
        existing_reservations = conn.execute(
            "SELECT * FROM reservations WHERE user_id = ? AND date BETWEEN ? AND ?",
            (user_id, start_week, end_week)
        ).fetchall()

        total_reserved_time = len(existing_reservations)

        if role == "client" and total_reserved_time >= 3:
            flash("Vous avez déjà réservé 3 heures cette semaine. Limite atteinte.")
        else:
            # Vérifier si ce créneau est déjà réservé
            existing_reservation = conn.execute(
                "SELECT * FROM reservations WHERE stadium_id = ? AND date = ? AND time = ?",
                (stadium_id, reservation_date, reservation_time)
            ).fetchone()

            if existing_reservation:
                flash("Ce créneau est déjà réservé.")
            else:
                # Insérer la réservation
                conn.execute(
                    "INSERT INTO reservations (stadium_id, user_id, date, time) VALUES (?, ?, ?, ?)",
                    (stadium_id, user_id, reservation_date, reservation_time)
                )
                conn.commit()
                flash("Réservation réussie.")


    # Récupérer toutes les réservations de ce stade
    reservations = conn.execute("SELECT * FROM reservations WHERE stadium_id = ?", (stadium_id,)).fetchall()

    # Récupérer les réservations de l'utilisateur connecté pour annulation
    user_reservations = conn.execute(
        "SELECT * FROM reservations WHERE user_id = ? AND stadium_id = ?",
        (user_id, stadium_id)
    ).fetchall()

    # Préparer les données du calendrier
    today = datetime.today().date()
    calendar_days = [today + timedelta(days=i) for i in range(7)]
    hours = [f"{h:02d}:00" for h in range(8, 19)]

    # Dictionnaire pour l'état des créneaux
    calendar = {day.strftime('%Y-%m-%d'): {hour: "free" for hour in hours} for day in calendar_days}

    for res in reservations:
        res_date = res["date"]
        res_time = res["time"]
        res_user = res["user_id"]

        # Marque le créneau comme réservé ou trainer
        if res_date in calendar and res_time in calendar[res_date]:
            calendar[res_date][res_time] = "reserved"

    conn.close()

    return render_template("stadium_details.html",
                        stadium=stadium,
                        reservations=reservations,
                        user_reservations=user_reservations,
                        calendar_days=calendar_days,
                        hours=hours,
                        calendar=calendar)

@app.route("/stadium/<int:stadium_id>", methods=["GET", "POST"])
def view_calendar(stadium_id):
    conn = get_db_connection()
    stadium = conn.execute("SELECT * FROM stadiums WHERE id = ?", (stadium_id,)).fetchone()

    if not stadium:
        flash("Stade introuvable")
        return redirect(url_for("index"))

    # Date sélectionnée (par défaut aujourd'hui)
    selected_date = request.args.get("date")
    if not selected_date:
        selected_date = datetime.today().strftime("%Y-%m-%d")

    # Récupère toutes les réservations pour cette date
    reservations = conn.execute("""
        SELECT * FROM reservations
        WHERE stadium_id = ? AND date = ?
    """, (stadium_id, selected_date)).fetchall()

    conn.close()

    # Créneaux horaires de 8h à 18h
    time_slots = [f"{h:02d}:00" for h in range(8, 19)]
    reserved_slots = {r["time"]: r for r in reservations}

    return render_template("calendar.html",
                        stadium=stadium,
                        selected_date=selected_date,
                        time_slots=time_slots,
                        reserved_slots=reserved_slots)

def view_calendar2(stadium_id):
    conn = get_db_connection()
    stadium = conn.execute("SELECT * FROM stadiums WHERE id = ?", (stadium_id,)).fetchone()

    if not stadium:
        flash("Stade introuvable")
        return redirect(url_for("index"))

    # Date sélectionnée (par défaut aujourd'hui)
    selected_date = request.args.get("date")
    if not selected_date:
        selected_date = datetime.today().strftime("%Y-%m-%d")


    # Récupère toutes les réservations pour cette date
    reservations = conn.execute("""
        SELECT * FROM reservations
        WHERE stadium_id = ? AND date = ?
    """, (stadium_id, selected_date)).fetchall()

    conn.close()

    # Créneaux horaires de 8h à 18h
    time_slots = [f"{h:02d}:00" for h in range(8, 19)]
    reserved_slots = {r["time"]: r for r in reservations}

@app.route("/reserve", methods=["POST"])
def reserve():
    if "user_id" not in session:
        flash("Connectez-vous pour réserver.")
        return redirect(url_for("login"))

    user_id = session["user_id"]
    date = request.form["date"]
    time = request.form["time"]
    stadium_id = request.form["stadium_id"]

    conn = get_db_connection()

    # Vérifier les conflits
    conflict = conn.execute("""
        SELECT * FROM reservations WHERE stadium_id = ? AND date = ? AND time = ?
    """, (stadium_id, date, time)).fetchone()

    if conflict:
        flash("Ce créneau est déjà réservé.")
        return redirect(url_for("view_calendar", stadium_id=stadium_id, date=date))

    # Vérifier limite client : max 3h/jour
    role = conn.execute("SELECT role FROM users WHERE id = ?", (user_id,)).fetchone()["role"]
    if role == "client":
        total_today = conn.execute("""
            SELECT COUNT(*) as count FROM reservations
            WHERE user_id = ? AND date = ?
        """, (user_id, date)).fetchone()["count"]
        if total_today >= 3:
            flash("Limite de 3 heures atteinte pour aujourd'hui.")
            return redirect(url_for("view_calendar", stadium_id=stadium_id, date=date))

    # Ajouter la réservation
    conn.execute("""
        INSERT INTO reservations (user_id, stadium_id, date, time)
        VALUES (?, ?, ?, ?)
    """, (user_id, stadium_id, date, time))
    conn.commit()
    conn.close()

    flash("Créneau réservé avec succès.")
    return redirect(url_for("view_calendar", stadium_id=stadium_id, date=date))


@app.route('/admin/stadiums')
def admin_stadiums():
    if session.get('role') != 'admin':
        return redirect(url_for('index'))
    conn = get_db()
    stadiums = conn.execute("SELECT * FROM stadiums").fetchall()
    return render_template('admin_stadiums.html', stadiums=stadiums)


if __name__ == '__main__':
    app.run(debug=True)