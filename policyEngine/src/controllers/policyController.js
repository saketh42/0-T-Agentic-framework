const { evaluatePolicyDecision } = require("../services/policyService");

function checkToolCall(req, res) {
  try {
    const { agent, request } = req.body;

    if (!agent || !request) {
      return res.status(400).json({
        error: 'Request body must include both "agent" and "request" objects'
      });
    }

    console.log("Received policy check request:", {
      agent_id: agent.agent_id,
      tool: request.tool,
      action: request.action
    });

    const result = evaluatePolicyDecision(agent, request);

    return res.status(200).json(result);
  } catch (error) {
    console.error("Controller error:", error.message);

    return res.status(500).json({
      error: "Failed to evaluate policy"
    });
  }
}

module.exports = {
  checkToolCall
};
