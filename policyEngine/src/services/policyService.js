const fs = require("fs");
const path = require("path");
const { matchesAllConditions } = require("../utils/conditionMatcher");

const policiesPath = path.join(__dirname, "../policies/policies.json");

function loadPolicies() {
  const rawPolicies = fs.readFileSync(policiesPath, "utf-8");
  return JSON.parse(rawPolicies);
}

function buildEvaluationContext(agent, request) {
  const toolAllowed = Array.isArray(agent.allowed_tools)
    ? agent.allowed_tools.includes(request.tool)
    : false;

  return {
    ...agent,
    ...request,
    tool_allowed: toolAllowed
  };
}

function evaluatePolicyDecision(agent, request) {
  const policies = loadPolicies();
  const context = buildEvaluationContext(agent, request);

  console.log("Policy evaluation context:", context);

  for (const policy of policies) {
    if (matchesAllConditions(policy.conditions, context)) {
      console.log(`Matched policy: ${policy.policy_id}`);

      return {
        decision: policy.decision,
        policy_id: policy.policy_id,
        reason: policy.reason
      };
    }
  }

  console.log("No policy matched. Returning default deny decision.");

  return {
    decision: "DENY",
    policy_id: "POLICY-DEFAULT-DENY",
    reason: "No policy matched the request context"
  };
}

module.exports = {
  evaluatePolicyDecision,
  buildEvaluationContext
};
