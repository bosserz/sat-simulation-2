import os
from app import db
from app import User, TestSession  # import your models

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 1) Local SQLite engine (read-only source)
SQLITE_URL = "sqlite:///sat_practice.db"   # adjust if needed
src_engine = create_engine(SQLITE_URL)
SrcSession = sessionmaker(bind=src_engine)
src_sess = SrcSession()

# 2) Remote Postgres engine (Render)
PG_URL = os.environ["DATABASE_URL"]
if PG_URL.startswith("postgres://"):
    PG_URL = PG_URL.replace("postgres://", "postgresql+psycopg2://", 1)
dst_engine = create_engine(PG_URL, connect_args={"sslmode": "require"})
DstSession = sessionmaker(bind=dst_engine)
dst_sess = DstSession()

def copy_users():
    print("Copying users...")
    src_users = src_sess.query(User).all()
    for u in src_users:
        # If you use autoincrement IDs and want to preserve IDs:
        # make sure your PG sequence is reset later (see note below)
        clone = User(
            id=u.id,                     # keep if you want same IDs
            email=u.email,
            password_hash=u.password_hash,
            # add other fields...
            created_at=u.created_at,
            updated_at=u.updated_at
        )
        dst_sess.merge(clone)  # upsert by PK
    dst_sess.commit()
    print(f"Copied {len(src_users)} users.")

def copy_sessions():
    print("Copying test sessions...")
    src_sessions = src_sess.query(TestSession).all()
    for s in src_sessions:
        clone = TestSession(
            id=s.id,                 # keep if desired
            user_id=s.user_id,       # must match copied user IDs
            test_name=s.test_name,
            status=s.status,
            score=s.score,
            started_at=s.started_at,
            finished_at=s.finished_at,
            # ... any JSON/text fields too
        )
        dst_sess.merge(clone)
    dst_sess.commit()
    print(f"Copied {len(src_sessions)} sessions.")

if __name__ == "__main__":
    copy_users()
    copy_sessions()
    print("Done.")
