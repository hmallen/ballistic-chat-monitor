require("dotenv").config({ path: "../.env" });

const express = require("express");
const http = require("http");
const socketIo = require("socket.io");

// eslint-disable-next-line no-undef
const port = process.env.PORT || 4001;
//const index = require("./routes/index");

// NEW
const bodyParser = require("body-parser");
const cors = require("cors");
const db = require("./db");
const userRouter = require("./routes/user-route");
const userCtrl = require("./controllers/user-ctrl");

const app = express();

//app.use(index);
app.use(userRouter);
//app.use(userCtrl);
app.use(bodyParser.urlencoded({ extended: true }));
app.use(cors());
app.use(bodyParser.json());

db.on("error", console.error.bind(console, "MongoDB connection error:"));

//app.use("/dashboard", userRouter);

const server = http.createServer(app);

const io = socketIo(server);

let interval;

io.on("connection", (socket) => {
  console.log("New client connected");
  if (interval) {
    clearInterval(interval);
  }
  interval = setInterval(() => getApiAndEmit(socket), 1000);
  socket.on("disconnect", () => {
    console.log("Client disconnected");
    clearInterval(interval);
  });
});

const getApiAndEmit = (socket) => {
  //const response = new Date();
  const response = userCtrl.getDashboard;
  // Emitting a new message. Will be consumed by the client
  socket.emit("FromAPI", response);
};

server.listen(port, () => console.log(`Listening on port ${port}`));
