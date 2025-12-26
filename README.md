# Axigen Multi‑Server Monitoring & Reporting

This project collects domain and mailbox quota data from one or more **Axigen Mail Servers**, stores periodic snapshots in PostgreSQL using **Async SQLAlchemy**, and exposes the data via **FastAPI** APIs. The system is designed to scale from 1 to ~100 servers and supports clean re‑polling (delete + insert) per server.

---

## 🏗️ Architecture Overview

**3‑Tier Architecture**

1. **Poller Layer (Python async scripts)**

   * Connects to Axigen servers (CLI + WebAdmin)
   * Collects domains, accounts, quotas
   * Populates PostgreSQL

2. **Backend API (FastAPI)**

   * Async SQLAlchemy ORM
   * APIs for servers, reports, domains, accounts

3. **Frontend (Planned)**

   * React + Vite 

---

## ⚙️ Requirements

* Python **3.13**
* PostgreSQL **13+**
* Axigen Mail Server (CLI + WebAdmin enabled)

Python packages (installed via `requirements.txt`):

* fastapi
* uvicorn
* sqlalchemy[asyncio]
* asyncpg
* cryptography
* python-dotenv

---

## 🔐 Environment Variables

Create a `.env` file in project root:

```env
DATABASE_URL=postgresql+asyncpg://axigen_user:password@localhost:5432/axigen_db
FERNET_KEY=your_generated_fernet_key
```

Generate Fernet key:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

---

## 🗄️ Database Setup

This project uses **Alembic** for database migrations.

### 1️⃣ Create Database & User

```sql
CREATE DATABASE axigen_db;
CREATE USER axigen_user WITH PASSWORD 'strongpassword';
GRANT ALL PRIVILEGES ON DATABASE axigen_db TO axigen_user;
```

Enable UUID extension:

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

---

### 2️⃣ Initialize Alembic (one time)

From project root:

```bash
alembic init alembic
```

Update **alembic.ini**:

```ini
s[alembic]
script_location = backend/alembic
prepend_sys_path = .

# We'll read DB URL from env via env.py, so keep this placeholder:
sqlalchemy.url = driver://user:pass@localhost/dbname

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = INFO
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s

```

Update **alembic/env.py**:

```python
import os
import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

# Alembic Config object
config = context.config

# Logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# IMPORTANT: import your Base + models so Alembic sees metadata
from backend.app.db.base import Base  # noqa
import backend.app.db.models  # noqa  (ensures tables are registered)

target_metadata = Base.metadata


def get_database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise ValueError("DATABASE_URL is not set in the environment or .env file")
    return url


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode with AsyncEngine."""
    url = get_database_url()

    connectable = create_async_engine(
        url,
        poolclass=pool.NullPool,
        connect_args={"ssl": False},
    )

    async with connectable.connect() as async_conn:
        await async_conn.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())

```

---

### 3️⃣ Create Initial Migration

```bash
alembic revision --autogenerate -m "initial schema"
```

Apply migration:

```bash
alembic upgrade head
```

---

## 🚀 Running the Backend API

Activate virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

Install dependencies:

```bash
pip install -r backend/requirements.txt
```

Start FastAPI server:

```bash
uvicorn backend.app.main:app --reload
```

API will be available at:

```text
http://localhost:8000
http://localhost:8000/docs
```

---

## 🖥️ Server Management APIs

### ➕ Add Server

```http
POST /add_server
```

```json
{
  "name": "Podbeez-Inam",
  "hostname": "203.175.66.162",
  "cli_port": 7000,
  "webadmin_port": 9000,
  "username": "admin",
  "password": "secret"
}
```

### ➖ Delete Server (by hostname)

```http
DELETE /delete_server
```

```json
{
  "hostname": "203.175.66.162"
}
```

---

## 🔄 Running the Poller

The poller:

* Iterates all servers in DB
* Deletes domains/accounts **per server**
* Re‑inserts fresh snapshot data
* Continues even if one server fails

Run manually:

```bash
python -m backend.app.poller.run_poller
```

Recommended via cron:

```bash
0 * * * * /path/to/venv/bin/python -m backend.app.poller.run_poller
```

---

## 📊 Reporting APIs

### Full Report (All Servers)

```http
GET /report
```

### Filter by Domain

```http
GET /report?domain=kohli.in
```

### Filter by Account

```http
GET /report?account=virat@kohli.in
```

---

## 🧠 Design Decisions

* **Async SQLAlchemy** only (no raw SQL)
* **TRUNCATE‑like behavior per server** (delete + insert)
* **Encrypted server passwords** (Fernet)
* **Snapshot‑based reporting**
* **Graceful error handling per server**

---

## 🧩 Next Steps

* Add authentication (JWT)
* Add scheduler inside app
---

## 👤 Author

Built by **Inam Rehman** — DevOps / Systems / Cloud Engineering project.

---


