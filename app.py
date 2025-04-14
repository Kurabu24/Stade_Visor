from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
app.secret_key = 'secret-key'
DATABASE = 'stadevisor.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/toggle-dark-mode', methods=['POST'])
def toggle_dark_mode():
    current = session.get('dark_mode', False)
    session['dark_mode'] = not current
    return jsonify({'dark_mode': session['dark_mode']})

def get_week_range(date_str):
    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    start_of_week = date_obj - timedelta(days=date_obj.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    return start_of_week, end_of_week

# Auth route (fusion de login et register)
@app.route("/auth", methods=["GET", "POST"])
def auth():
    if request.method == "POST":
        form_type = request.form.get("form_type")

        if form_type == "login":
            email = request.form.get("email")
            password = request.form.get("password")

            conn = get_db_connection()
            user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

            if user and check_password_hash(user["password_hash"], password):
                session["user_id"] = user["id"]
                session["role"] = user["role"]
                flash("Connexion réussie")
                conn.close()
                if user["role"] == "admin":
                    return redirect(url_for("admin_dashboard"))
                return redirect(url_for("index"))
            else:
                flash("Identifiants incorrects")
                conn.close()
                return redirect(url_for("auth"))

        elif form_type == "register":
            email = request.form.get("email")
            password = request.form.get("password")
            password_confirm = request.form.get("password_confirm")

            if not email or not password or not password_confirm:
                flash("Tous les champs sont requis")
                return redirect(url_for("auth"))

            if password != password_confirm:
                flash("Les mots de passe ne correspondent pas")
                return redirect(url_for("auth"))

            conn = get_db_connection()
            existing_user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

            if existing_user:
                flash("Cet email est déjà utilisé")
                conn.close()
                return redirect(url_for("auth"))

            hashed_password = generate_password_hash(password)
            conn.execute("INSERT INTO users (email, password_hash, role) VALUES (?, ?, ?)",
                         (email, hashed_password, "client"))
            conn.commit()
            conn.close()

            flash("Compte créé avec succès. Vous pouvez maintenant vous connecter.")
            return redirect(url_for("auth"))

    return render_template("auth.html")

@app.route('/logout')
def logout():
    session.clear()
    flash("Vous avez été déconnecté.")
    return redirect(url_for('index'))

@app.route("/")
def index():
    user_id = session.get("user_id")
    role = session.get("role")
    conn = get_db_connection()
    stadiums = conn.execute("SELECT * FROM stadiums").fetchall()
    conn.close()

    return render_template("index.html", role=role, stadiums=stadiums)

# Admin routes
@app.route("/admin/stadium/create", methods=["GET", "POST"])
def create_stadium():
    if session.get("role") != "admin":
        flash("Accès réservé à l'administrateur.")
        return redirect(url_for("index"))

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
        except Exception as e:
            flash(f"Erreur : {e}")
        finally:
            conn.close()

    return render_template("admin.html")

@app.route("/admin")
def admin_dashboard():
    if session.get("role") != "admin":
        flash("Accès réservé à l'administrateur.")
        return redirect(url_for("index"))

    conn = get_db_connection()
    users = conn.execute("SELECT * FROM users").fetchall()
    stadiums = conn.execute("SELECT * FROM stadiums").fetchall()
    reservations = conn.execute("SELECT * FROM reservations").fetchall()
    conn.close()
    return render_template("admin_dashboard.html", users=users, stadiums=stadiums, reservations=reservations)

@app.route("/admin/delete_all_reservations", methods=["POST"])
def delete_all_reservations():
    if session.get("role") != "admin":
        flash("Accès réservé à l'administrateur.")
        return redirect(url_for("index"))

    conn = get_db_connection()
    conn.execute("DELETE FROM reservations")
    conn.commit()
    conn.close()
    flash("Toutes les réservations ont été supprimées.")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/add_stadium", methods=["POST"])
def add_stadium():
    if session.get("role") != "admin":
        flash("Accès réservé à l'administrateur.")
        return redirect(url_for("index"))

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
def delete_stadium(stadium_id):
    if session.get("role") != "admin":
        flash("Accès réservé à l'administrateur.")
        return redirect(url_for("index"))

    conn = get_db_connection()
    conn.execute("DELETE FROM reservations WHERE stadium_id = ?", (stadium_id,))
    conn.execute("DELETE FROM stadiums WHERE id = ?", (stadium_id,))
    conn.commit()
    conn.close()

    flash("Stade et ses réservations associées supprimés.", category='success')
    return redirect(url_for("admin_dashboard"))

@app.route('/admin/reservations/delete/<int:reservation_id>', methods=['POST'])
def delete_reservation(reservation_id):
    if session.get("role") != "admin":
        flash("Accès réservé à l'administrateur.")
        return redirect(url_for("index"))

    conn = get_db_connection()
    conn.execute('DELETE FROM reservations WHERE id = ?', (reservation_id,))
    conn.commit()
    conn.close()
    flash("Réservation supprimée.")
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/users/change_role/<int:user_id>', methods=['POST'])
def change_user_role(user_id):
    if session.get("role") != "admin":
        flash("Accès réservé à l'administrateur.")
        return redirect(url_for("index"))

    new_role = request.form['role']
    conn = get_db_connection()
    conn.execute('UPDATE users SET role = ? WHERE id = ?', (new_role, user_id))
    conn.commit()
    conn.close()
    flash(f"Rôle de l'utilisateur {user_id} modifié en {new_role}.")
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/stadiums')
def admin_stadiums():
    if session.get('role') != 'admin':
        flash("Accès réservé à l'administrateur.")
        return redirect(url_for('index'))
    conn = get_db_connection()
    stadiums = conn.execute("SELECT * FROM stadiums").fetchall()
    conn.close()
    return render_template('admin_stadiums.html', stadiums=stadiums)

# Reservation routes
@app.route("/stadium_details/<int:stadium_id>", methods=["GET", "POST"])
def stadium_details(stadium_id):
    user_id = session.get("user_id")
    role = session.get("role")

    if not user_id:
        flash("Vous devez être connecté pour accéder à cette page.")
        return redirect(url_for("auth"))

    conn = get_db_connection()
    stadium = conn.execute("SELECT * FROM stadiums WHERE id = ?", (stadium_id,)).fetchone()

    if not stadium:
        flash("Le stade n'existe pas.")
        conn.close()
        return redirect(url_for("index"))

    if request.method == "POST":
        reservation_date = request.form["date"]
        reservation_time = request.form["time"]

        start_week, end_week = get_week_range(reservation_date)

        existing_reservations = conn.execute(
            "SELECT * FROM reservations WHERE user_id = ? AND date BETWEEN ? AND ?",
            (user_id, start_week, end_week)
        ).fetchall()

        total_reserved_time = len(existing_reservations)

        if role == "client" and total_reserved_time >= 3:
            flash("Vous avez déjà réservé 3 heures cette semaine. Limite atteinte.")
        else:
            existing_reservation = conn.execute(
                "SELECT * FROM reservations WHERE stadium_id = ? AND date = ? AND time = ?",
                (stadium_id, reservation_date, reservation_time)
            ).fetchone()

            if existing_reservation:
                flash("Ce créneau est déjà réservé.")
            else:
                conn.execute(
                    "INSERT INTO reservations (stadium_id, user_id, date, time) VALUES (?, ?, ?, ?)",
                    (stadium_id, user_id, reservation_date, reservation_time)
                )
                conn.commit()
                flash("Réservation réussie.")

    today = datetime.today().date()
    calendar_days = [today + timedelta(days=i) for i in range(7)]
    hours = [f"{h:02d}:00" for h in range(8, 19)]

    reservations = conn.execute(
        "SELECT * FROM reservations WHERE stadium_id = ? AND date >= ? AND date <= ?",
        (stadium_id, calendar_days[0].strftime("%Y-%m-%d"), calendar_days[-1].strftime("%Y-%m-%d"))
    ).fetchall()

    user_reservations = conn.execute(
        "SELECT * FROM reservations WHERE user_id = ? AND stadium_id = ? AND date >= ? AND date <= ?",
        (user_id, stadium_id, calendar_days[0].strftime("%Y-%m-%d"), calendar_days[-1].strftime("%Y-%m-%d"))
    ).fetchall() if user_id else []

    calendar = {day.strftime('%Y-%m-%d'): {hour: "free" for hour in hours} for day in calendar_days}
    for res in reservations:
        res_date = res["date"]
        res_time = res["time"]
        if res_date in calendar and res_time in calendar[res_date]:
            calendar[res_date][res_time] = "reserved"

    conn.close()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template(
            '/tableau_stadium_details.html',
            stadium=stadium,
            calendar_days=calendar_days,
            hours=hours,
            calendar=calendar,
            user_reservations=user_reservations,
            role=role
        )

    return render_template(
        "stadium_details.html",
        stadium=stadium,
        calendar_days=calendar_days,
        hours=hours,
        calendar=calendar,
        user_reservations=user_reservations,
        role=role
    )

@app.route("/calendar/<int:stadium_id>", methods=["GET", "POST"])
def view_calendar(stadium_id):
    conn = get_db_connection()
    stadium = conn.execute("SELECT * FROM stadiums WHERE id = ?", (stadium_id,)).fetchone()

    if not stadium:
        flash("Stade introuvable")
        conn.close()
        return redirect(url_for("index"))

    selected_date = request.args.get("date")
    if not selected_date:
        selected_date = datetime.today().strftime("%Y-%m-%d")

    if request.method == "POST":
        user_id = session.get("user_id")
        if not user_id:
            flash("Vous devez être connecté pour réserver.")
            conn.close()
            return redirect(url_for("auth"))

        date = request.form["date"]
        time = request.form["time"]

        existing_reservation = conn.execute(
            "SELECT * FROM reservations WHERE stadium_id = ? AND date = ? AND time = ?",
            (stadium_id, date, time)
        ).fetchone()

        if existing_reservation:
            flash("Ce créneau est déjà réservé.")
        else:
            role = conn.execute("SELECT role FROM users WHERE id = ?", (user_id,)).fetchone()["role"]
            if role == "client":
                start_week, end_week = get_week_range(date)
                total_week = conn.execute(
                    "SELECT COUNT(*) as count FROM reservations WHERE user_id = ? AND date BETWEEN ? AND ?",
                    (user_id, start_week, end_week)
                ).fetchone()["count"]
                if total_week >= 3:
                    flash("Limite de 3 heures par semaine atteinte.")
                    conn.close()
                    return redirect(url_for("view_calendar", stadium_id=stadium_id, date=date))

            conn.execute(
                "INSERT INTO reservations (stadium_id, user_id, date, time) VALUES (?, ?, ?, ?)",
                (stadium_id, user_id, date, time)
            )
            conn.commit()
            flash("Réservation effectuée avec succès.")

    reservations = conn.execute(
        "SELECT * FROM reservations WHERE stadium_id = ? AND date = ?",
        (stadium_id, selected_date)
    ).fetchall()

    time_slots = [f"{h:02d}:00" for h in range(8, 19)]
    reserved_slots = {r["time"]: r for r in reservations}

    conn.close()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template(
            '/tableau_reservations.html',
            time_slots=time_slots,
            reserved_slots=reserved_slots,
            stadium=stadium,
            selected_date=selected_date
        )

    return render_template(
        "calendar.html",
        stadium=stadium,
        selected_date=selected_date,
        time_slots=time_slots,
        reserved_slots=reserved_slots
    )

@app.route("/cancel_reservation", methods=["POST"])
def cancel_reservation():
    user_id = session.get("user_id")
    if not user_id:
        flash("Vous devez être connecté pour annuler une réservation.")
        return redirect(url_for("auth"))

    reservation_id = request.form["reservation_id"]
    stadium_id = request.form["stadium_id"]

    conn = get_db_connection()
    reservation = conn.execute(
        "SELECT * FROM reservations WHERE id = ? AND user_id = ?",
        (reservation_id, user_id)
    ).fetchone()

    if reservation:
        conn.execute("DELETE FROM reservations WHERE id = ?", (reservation_id,))
        conn.commit()
        flash("Réservation annulée avec succès.")
    else:
        flash("Aucune réservation trouvée ou vous ne pouvez pas l'annuler.")

    conn.close()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({"success": True, "stadium_id": stadium_id})

    return redirect(url_for("stadium_details", stadium_id=stadium_id))

@app.route("/reserve", methods=["POST"])
def reserve():
    if "user_id" not in session:
        flash("Connectez-vous pour réserver.")
        return redirect(url_for("auth"))

    user_id = session["user_id"]
    date = request.form["date"]
    time = request.form["time"]
    stadium_id = request.form["stadium_id"]

    conn = get_db_connection()

    existing_reservation = conn.execute(
        "SELECT * FROM reservations WHERE stadium_id = ? AND date = ? AND time = ?",
        (stadium_id, date, time)
    ).fetchone()

    if existing_reservation:
        flash("Ce créneau est déjà réservé.")
        conn.close()
        return redirect(url_for("view_calendar", stadium_id=stadium_id, date=date))

    role = conn.execute("SELECT role FROM users WHERE id = ?", (user_id,)).fetchone()["role"]
    if role == "client":
        start_week, end_week = get_week_range(date)
        total_week = conn.execute(
            "SELECT COUNT(*) as count FROM reservations WHERE user_id = ? AND date BETWEEN ? AND ?",
            (user_id, start_week, end_week)
        ).fetchone()["count"]
        if total_week >= 3:
            flash("Limite de 3 heures par semaine atteinte.")
            conn.close()
            return redirect(url_for("view_calendar", stadium_id=stadium_id, date=date))

    conn.execute(
        "INSERT INTO reservations (user_id, stadium_id, date, time) VALUES (?, ?, ?, ?)",
        (user_id, stadium_id, date, time)
    )
    conn.commit()
    conn.close()

    flash("Créneau réservé avec succès.")
    return redirect(url_for("view_calendar", stadium_id=stadium_id, date=date))

if __name__ == '__main__':
    app.run(debug=True)