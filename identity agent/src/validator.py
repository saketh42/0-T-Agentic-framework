def validate_request(request):

    print("[Validator] Validating incoming request")

    if not request.agent_id:
        raise ValueError("agent_id missing")

    if not request.session_id:
        raise ValueError("session_id missing")

    if not request.environment:
        raise ValueError("environment missing")

    print("[Validator] Request structure valid")

    return True
