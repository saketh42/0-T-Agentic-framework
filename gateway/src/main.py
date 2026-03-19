from fastapi import FastAPI

from gateway.src.routers.gateway import router as gateway_router


app = FastAPI(
    title="Security & Privacy Gateway",
    version="0.1.0",
    description="Gateway backend for identity, policy, DLP, and audit checks."
)

app.include_router(gateway_router)


@app.get("/")
def root():
    return {
        "service": "security-privacy-gateway",
        "status": "running"
    }
