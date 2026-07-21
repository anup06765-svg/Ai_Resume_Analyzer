from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autoflush=False,
    autocommit=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    Base.metadata.create_all(bind=engine)
    _run_light_migrations()


def _run_light_migrations():
    """
    Purani SQLite tables me naye columns add karta hai
    agar wo pehle se maujood nahi hain.
    """

    if not DATABASE_URL.startswith("sqlite"):
        return

    from sqlalchemy import text

    migrations = {
        "users": [
            ("role", "VARCHAR(20) NOT NULL DEFAULT 'candidate'"),
        ],
        "resumes": [
            ("hr_profile_id", "INTEGER"),
            ("candidate_name", "VARCHAR(150)"),
            ("is_shortlisted", "BOOLEAN NOT NULL DEFAULT 0"),
            ("jd_match_score", "INTEGER"),
            ("jd_matched_skills", "TEXT"),
            ("jd_missing_skills", "TEXT"),
            ("combined_score", "INTEGER NOT NULL DEFAULT 0"),
        ],
    }

    with engine.connect() as conn:
        for table, columns in migrations.items():

            existing = {
                row[1]
                for row in conn.execute(text(f"PRAGMA table_info({table})"))
            }

            for column_name, column_def in columns:
                if column_name not in existing:
                    conn.execute(
                        text(
                            f"ALTER TABLE {table} "
                            f"ADD COLUMN {column_name} {column_def}"
                        )
                    )

        conn.commit()