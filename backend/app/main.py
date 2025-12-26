from fastapi import FastAPI

from backend.app.api.servers import router as servers_router
from backend.app.api.domains import router as domains_router
from backend.app.api.accounts import router as accounts_router
from backend.app.api.dashboard import router as dashboard_router
from backend.app.api.summary import router as summary_router
from backend.app.api.report import router as report_router
from backend.app.api.add_server import router as add_server_router
from backend.app.api.delete_server import router as delete_server_router
from backend.app.api import add_server, jobs
#from backend.app.api import servers, domains, accounts, summary
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Axigen Multi-Server API", routes=[],redirect_slashes=False)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Your Vite dev server
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
app.include_router(add_server_router)
app.include_router(delete_server_router)
app.include_router(jobs.router)

@app.get("/")
def root():
    return {"status": "ok", "message": "Axigen API is running"}
