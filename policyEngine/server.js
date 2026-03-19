const express = require("express");
const toolCheckRoutes = require("./src/routes/toolCheckRoutes");

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());

app.get("/", (req, res) => {
  res.json({
    message: "Policy Engine PDP is running"
  });
});

app.use("/", toolCheckRoutes);

app.use((err, req, res, next) => {
  console.error("Unhandled error:", err);

  res.status(500).json({
    error: "Internal server error"
  });
});

app.listen(PORT, () => {
  console.log(`Policy Engine server running on port ${PORT}`);
});
