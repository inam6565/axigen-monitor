from fastapi import FastAPI

from backend.app.api.servers import router as servers_router
from backend.app.api.domains import router as domains_router
from backend.app.api.accounts import router as accounts_router
from backend.app.api.dashboard import router as dashboard_router
from backend.app.api.summary import router as summary_router
from backend.app.api.report import router as report_router
#from backend.app.api import servers, domains, accounts, summary
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Axigen Multi-Server API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Your Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(servers_router)
app.include_router(domains_router)
app.include_router(accounts_router)
app.include_router(dashboard_router)
app.include_router(summary_router)
app.include_router(report_router) 

@app.get("/")
def root():
    return {"status": "ok", "message": "Axigen API is running"}
