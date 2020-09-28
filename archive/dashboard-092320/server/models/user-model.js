const mongoose = require("mongoose");
const Schema = mongoose.Schema;

const CountSchema = new Schema({
  name: { type: String, required: true },
  count: { type: Number, required: true },
});

const UserSchema = new Schema({
  users: [CountSchema],
});

module.exports = mongoose.model("users", UserSchema);
