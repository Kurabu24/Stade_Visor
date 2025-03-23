const db = require("./db");

function createStade(name, location, capacity, created_by) {
    return db
        .prepare("INSERT INTO stades (name, location, capacity, created_by) VALUES (?, ?, ?, ?)")
        .run(name, location, capacity, created_by);
}

function getAllStades() {
    return db.prepare("SELECT * FROM stades").all();
}

function getStadeById(id) {
    return db.prepare("SELECT * FROM stades WHERE id = ?").get(id);
}

module.exports = { createStade, getAllStades, getStadeById };
