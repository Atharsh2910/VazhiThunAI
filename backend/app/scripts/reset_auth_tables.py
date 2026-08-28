import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.models.database import engine
from app.models.orm import Base

def reset_tables():
    print("Dropping users and learner_profiles tables...")
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS learner_profiles CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS users CASCADE;"))
    
    print("Recreating tables from ORM...")
    Base.metadata.create_all(bind=engine)
    print("Done! Auth tables reset with new schema.")

if __name__ == "__main__":
    reset_tables()
