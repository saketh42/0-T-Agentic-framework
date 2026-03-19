function matchCondition(condition, context) {
  const { field, operator, value } = condition;
  const actualValue = context[field];

  switch (operator) {
    case "equals":
      return actualValue === value;
    case "lte":
      return actualValue <= value;
    case "gt":
      return actualValue > value;
    default:
      console.warn(`Unsupported operator: ${operator}`);
      return false;
  }
}

function matchesAllConditions(conditions = [], context) {
  return conditions.every((condition) => matchCondition(condition, context));
}

module.exports = {
  matchCondition,
  matchesAllConditions
};
