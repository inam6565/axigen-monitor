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

## How to run

### 1. Install Docker

Ensure that Docker is installed on your system. If you haven't installed Docker yet, you can follow the installation instructions for your operating system from the official Docker documentation: [Docker Installation Guide](https://docs.docker.com/get-docker/).

### 2. Clone the Repository

Clone the `axigen-monitor` repository to your local machine by running the following command:

```bash
git clone https://github.com/inam6565/axigen-monitor.git
```
### 3. Checkout the Docker Branch

Navigate to the cloned repository folder and checkout the docker-first branch:

```bash
cd axigen-monitor
git checkout docker-first
```
### 4. Run the Application Using Docker Compose

Now, you can run the application using Docker Compose. Execute the following command to build and start the application:

```bash
docker compose up -d --build
```

### 5. Access the Application

Once the application is up and running, you can access it by navigating to:

```bash
http://your-server-ip:8080
```
Note: You can change the port by modifying the docker-compose.yml file if needed.
---

## 👤 Author

Built by **Inam Rehman** — DevOps / Systems / Cloud Engineering project.

---


