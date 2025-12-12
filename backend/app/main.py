from fastapi import FastAPI

from backend.app.api.servers import router as servers_router
from backend.app.api.domains import router as domains_router
from backend.app.api.accounts import router as accounts_router
from backend.app.api.dashboard import router as dashboard_router

app = FastAPI(title="Axigen Multi-Server API")

# Register routers
app.include_router(servers_router)
app.include_router(domains_router)
app.include_router(accounts_router)
app.include_router(dashboard_router)

@app.get("/")
def root():
    return {"status": "ok", "message": "Axigen API is running"}
