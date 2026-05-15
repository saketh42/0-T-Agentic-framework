"""
FastAPI server for Identity Agent

Usage:
    uvicorn src.api:app --host 0.0.0.0 --port 8000
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from postgres_client import PostgresIdentityAgentDatabaseClient
from stm_redis_client import RedisAgentShortTermMemoryClient
from identity_agent import identity_agent_service
from schemas import IdentityValidationRequest

app = FastAPI(title="Identity Agent API", version="1.0.0")

_db = None
_stm = None


def get_db():
    global _db
    if _db is None:
        _db = PostgresIdentityAgentDatabaseClient()
    return _db


def get_stm():
    global _stm
    if _stm is None:
        try:
            _stm = RedisAgentShortTermMemoryClient()
            _stm.redis_client.ping()
        except Exception:
            from stm_memory import MemoryAgentShortTermMemoryClient
            _stm = MemoryAgentShortTermMemoryClient()
    return _stm


@app.on_event("shutdown")
def shutdown():
    global _db, _stm
    if _db:
        _db.close()
    if _stm:
        try:
            _stm.redis_client.close()
        except Exception:
            pass


@app.get("/.well-known/jwks.json")
def jwks(kid: str = None):
    db = get_db()
    db.get_active_signing_key()
    keys = db.list_active_signing_keys()
    if kid:
        keys = [k for k in keys if k.kid == kid]

    from issue_jwt import pem_to_jwk

    jwks_list = []
    for key in keys:
        jwk = pem_to_jwk(key.public_key_pem)
        jwk.update({
            "use": "sig",
            "alg": key.algorithm,
            "kid": key.kid,
        })
        jwks_list.append(jwk)

    return JSONResponse({"keys": jwks_list})


@app.post("/validate")
def validate_identity(payload: IdentityValidationRequest):
    db = get_db()
    stm = get_stm()
    result = identity_agent_service(payload.model_dump(), db_client=db, stm_client=stm)

    headers = {}
    if result.identity_context and result.identity_context.token:
        import base64, json
        header_b64 = result.identity_context.token.split(".")[0]
        header_b64 += "=" * (4 - len(header_b64) % 4)
        kid = json.loads(base64.urlsafe_b64decode(header_b64)).get("kid")
        if kid:
            headers["X-KID"] = kid

    return JSONResponse(content=result.model_dump(mode="json"), headers=headers)


@app.get("/stm")
def stm_get_all():
    stm = get_stm()
    if hasattr(stm, '_sessions'):
        return {"sessions": {k: v for k, v in stm._sessions.items()}}
    import json
    keys = stm.redis_client.keys("*")
    sessions = {}
    for key in keys:
        raw = stm.redis_client.get(key)
        sessions[key] = json.loads(raw) if raw else None
    return sessions
