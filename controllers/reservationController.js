const reservationModel = require("../models/reservationModel");

function createReservation(req, res) {
    if (!req.session.user) return res.redirect("/login");

    const { stade_id, date, time } = req.body;
    reservationModel.createReservation(stade_id, req.session.user.id, date, time);
    res.redirect("/my_reservations");
}

function listReservations(req, res) {
    if (!req.session.user) return res.redirect("/login");

    const reservations = reservationModel.getReservationsByUser(req.session.user.id);
    res.render("my_reservations", { reservations });
}

module.exports = { createReservation, listReservations };
