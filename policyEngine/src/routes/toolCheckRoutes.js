const express = require("express");
const { checkToolCall } = require("../controllers/policyController");

const router = express.Router();

router.post("/check_tool_call", checkToolCall);

module.exports = router;
