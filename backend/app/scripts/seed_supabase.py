import os
import sys
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine

# Ensure we can import app modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.models.database import Base
from app.models.orm import *
from app.core.config import settings

def main():
    engine = create_engine(settings.DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    print("Tables created.")

    data_dir = Path(__file__).parent.parent.parent / "data"

    csv_mapping = [
        ("skills.csv", "skills"),
        ("learners.csv", "learners"),
        ("assessments.csv", "assessments"),
        ("resources.csv", "resources"),
        ("learner_skills.csv", "learner_skills"),
        ("assessment_attempts.csv", "assessment_attempts"),
        ("goals.csv", "goals"),
        ("learning_paths.csv", "learning_paths"),
        ("path_items.csv", "path_items"),
        ("projects.csv", "projects"),
        ("recommendation_events.csv", "recommendation_events"),
        ("resource_skills.csv", "resource_skills"),
        ("skill_prerequisites.csv", "skill_prerequisites"),
        ("chat_intent_dataset.csv", "chat_intent_dataset"),
        ("feedback_dataset.csv", "feedback_dataset")
    ]

    for csv_file, table_name in csv_mapping:
        file_path = data_dir / csv_file
        if not file_path.exists():
            print(f"File not found: {file_path}")
            continue
        print(f"Loading {csv_file} into {table_name}...")
        df = pd.read_csv(file_path)
        # Append data directly using pandas and SQLAlchemy
        df.to_sql(table_name, engine, if_exists="append", index=False)
        print(f"Inserted {len(df)} rows into {table_name}.")

if __name__ == "__main__":
    main()
