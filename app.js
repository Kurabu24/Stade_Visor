const express = require("express");
const mustacheExpress = require("mustache-express");
const bodyParser = require("body-parser");
const session = require("cookie-session");
const path = require("path");

const authRoutes = require("./routes/authRoutes");
const stadeRoutes = require("./routes/stadeRoutes");
const reservationRoutes = require("./routes/reservationRoutes");

const app = express();

// Configuration du moteur de template Mustache
app.engine("mustache", mustacheExpress());
app.set("view engine", "mustache");
app.set("views", path.join(__dirname, "views"));

// Middleware
app.use(bodyParser.urlencoded({ extended: false }));
app.use(express.static(path.join(__dirname, "public")));
app.use(
    session({
        name: "session",
        keys: ["secret"],
        maxAge: 24 * 60 * 60 * 1000,
    })
);

// Routes
app.use(authRoutes);
app.use(stadeRoutes);
app.use(reservationRoutes);

// Serveur
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Serveur démarré sur http://localhost:${PORT}`);
});
