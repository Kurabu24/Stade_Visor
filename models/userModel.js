const db = require("./db");

function createUser(email, password, role) {
    return db
        .prepare("INSERT INTO users (email, password, role) VALUES (?, ?, ?)")
        .run(email, password, role);
}

function getUserByEmail(email) {
    return db
        .prepare("SELECT * FROM users WHERE email = ?")
        .get(email);
}

module.exports = { createUser, getUserByEmail };
