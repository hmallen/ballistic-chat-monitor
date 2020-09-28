const express = require("express");

const UserCtrl = require("../controllers/user-ctrl");

const router = express.Router();

router.get("/stats", UserCtrl.getDashboard);

module.exports = router;
