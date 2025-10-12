import os
from app import app, db  # uses your existing app.py

if __name__ == "__main__":
    # Must have DATABASE_URL set to Render before running this
    with app.app_context():
        db.create_all()
        print("✅ Created tables on remote Postgres (Render).")