from app.db.base import SessionLocal
from app.poller.sync_runner import sync_all_servers

def main():
    db = SessionLocal()
    try:
        sync_all_servers(db)
    finally:
        db.close()

if __name__ == "__main__":
    main()
