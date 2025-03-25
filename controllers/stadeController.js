const stadeModel = require("../models/stadeModel");

function listStades(req, res) {
    const stades = stadeModel.getAllStades();
    res.render("index", { stades, user: req.session.user });
}

function createStade(req, res) {
    if (!req.session.user) return res.redirect("/login");

    const { name, location} = req.body;
    stadeModel.createStade(name, location , req.session.user.id);
    res.redirect("/");
}

module.exports = { listStades, createStade };
