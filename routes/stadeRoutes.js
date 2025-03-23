const express = require("express");
const router = express.Router();
const stadeController = require("../controllers/stadeController");

router.get("/", stadeController.listStades);
router.post("/stade/create", stadeController.createStade);

module.exports = router;
