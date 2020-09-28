const User = require("../models/user-model");

getDashboard = async (req, res) => {
  await User.findOne({ _id: "dashboard" }, (err, users) => {
    if (err) {
      return res.status(400).json({ success: false, error: err });
    }

    if (!users) {
      return res
        .status(404)
        .json({ success: false, error: "Dashboard not found." });
    }

    return res.status(200).json({ success: true, data: users });
  }).catch((err) => console.log(err));
};

module.exports = { getDashboard };
