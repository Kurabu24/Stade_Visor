const db = require("./db");

function createReservation(stade_id, user_id, date, time) {
    return db
        .prepare("INSERT INTO reservations (stade_id, user_id, date, time) VALUES (?, ?, ?, ?)")
        .run(stade_id, user_id, date, time);
}

function getReservationsByUser(user_id) {
    return db
        .prepare("SELECT reservations.*, stades.name FROM reservations JOIN stades ON reservations.stade_id = stades.id WHERE user_id = ?")
        .all(user_id);
}

module.exports = { createReservation, getReservationsByUser };
