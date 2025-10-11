"""
Data migration script to transfer data from SQLite to PostgreSQL
Run this script after setting up your PostgreSQL database on Render
"""

import sqlite3
import os
from app import app, db, User, TestSession

def migrate_data():
    """Migrate data from SQLite to PostgreSQL"""
    
    # Check if SQLite database exists
    sqlite_path = 'instance/sat_practice.db'
    if not os.path.exists(sqlite_path):
        print("No SQLite database found to migrate from.")
        return
    
    # Connect to SQLite database
    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_conn.row_factory = sqlite3.Row
    cursor = sqlite_conn.cursor()
    
    with app.app_context():
        # Create all tables in PostgreSQL
        db.create_all()
        
        try:
            # Migrate users
            cursor.execute("SELECT * FROM user")
            users = cursor.fetchall()
            
            for user_row in users:
                # Check if user already exists
                existing_user = User.query.filter_by(username=user_row['username']).first()
                if not existing_user:
                    user = User(
                        username=user_row['username'],
                        password=user_row['password'],
                        email=user_row['email']
                    )
                    db.session.add(user)
            
            db.session.commit()
            print(f"Migrated {len(users)} users")
            
            # Migrate test sessions
            cursor.execute("SELECT * FROM test_session")
            sessions = cursor.fetchall()
            
            for session_row in sessions:
                # Find the corresponding user in PostgreSQL
                user = User.query.filter_by(username=users[session_row['user_id']-1]['username']).first()
                if user:
                    # Check if session already exists
                    existing_session = TestSession.query.filter_by(
                        user_id=user.id,
                        practice_test_id=session_row['practice_test_id'],
                        start_time=session_row['start_time']
                    ).first()
                    
                    if not existing_session:
                        test_session = TestSession(
                            user_id=user.id,
                            practice_test_id=session_row['practice_test_id'],
                            start_time=session_row['start_time'],
                            score=session_row['score'],
                            answers=session_row['answers'],
                            current_question=session_row['current_question'],
                            current_section=session_row['current_section'],
                            marked_for_review=session_row['marked_for_review'],
                            section_start_time=session_row['section_start_time']
                        )
                        db.session.add(test_session)
            
            db.session.commit()
            print(f"Migrated {len(sessions)} test sessions")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error during migration: {e}")
            raise
        
        finally:
            sqlite_conn.close()

if __name__ == '__main__':
    migrate_data()