const bcrypt = require("bcryptjs");
const userModel = require("../models/userModel");

async function register(req, res) {
    const { email, password } = req.body;
    const hashedPassword = await bcrypt.hash(password, 10);
    userModel.createUser(email, hashedPassword, "user");
    res.redirect("/login");
}

async function login(req, res) {
    const { email, password } = req.body;
    const user = userModel.getUserByEmail(email);

    if (user && (await bcrypt.compare(password, user.password))) {
        req.session.user = { id: user.id, email: user.email, role: user.role };
        res.redirect("/");
    } else {
        res.send("Identifiants incorrects.");
    }
}

function logout(req, res) {
    req.session = null;
    res.redirect("/login");
}

module.exports = { register, login, logout };
