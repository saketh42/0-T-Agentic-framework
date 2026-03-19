from gateway.src.schemas.responses import GatewayResponse
from gateway.src.services.identity_bridge import resolve_gateway_identity


def handle_identity_check(payload):
    identity_result = resolve_gateway_identity(payload)

    return GatewayResponse(
        stage="identity",
        decision=identity_result["decision"],
        reason=identity_result["reason"],
        request_type="identity",
        identity=identity_result,
        next_step="policy" if identity_result["decision"] == "allow" else "stop",
        notes=["Identity check completed through gateway."]
    )


def handle_plan_check(payload):
    identity_result = resolve_gateway_identity(payload)

    notes = ["Plan received by gateway."]
    if identity_result["decision"] == "allow":
        notes.append("Identity verified. Plan is ready for policy evaluation.")
        next_step = "policy"
    else:
        notes.append("Plan stopped during identity verification.")
        next_step = "stop"

    return GatewayResponse(
        stage="identity",
        decision=identity_result["decision"],
        reason=identity_result["reason"],
        request_type="plan",
        identity=identity_result,
        next_step=next_step,
        notes=notes
    )


def handle_tool_call_check(payload):
    identity_result = resolve_gateway_identity(payload)

    notes = [f"Tool call requested for {payload.tool_name}."]
    if identity_result["decision"] == "allow":
        notes.append("Identity verified. Tool call is ready for policy evaluation.")
        next_step = "policy"
    else:
        notes.append("Tool call stopped during identity verification.")
        next_step = "stop"

    return GatewayResponse(
        stage="identity",
        decision=identity_result["decision"],
        reason=identity_result["reason"],
        request_type="tool_call",
        identity=identity_result,
        next_step=next_step,
        notes=notes
    )


def handle_io_check(payload):
    identity_result = resolve_gateway_identity(payload)

    notes = [f"IO request received for {payload.io_type}."]
    if identity_result["decision"] == "allow":
        notes.append("Identity verified. IO request is ready for DLP and policy checks.")
        next_step = "dlp"
    else:
        notes.append("IO request stopped during identity verification.")
        next_step = "stop"

    return GatewayResponse(
        stage="identity",
        decision=identity_result["decision"],
        reason=identity_result["reason"],
        request_type="io",
        identity=identity_result,
        next_step=next_step,
        notes=notes
    )
