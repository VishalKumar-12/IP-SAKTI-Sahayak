"""
One-off script to create all database tables in PostgreSQL.

Usage:
    python -m scripts.init_db

Make sure DATABASE_URL (or DB_HOST/DB_PORT/DB_NAME/DB_USER/DB_PASSWORD)
is set correctly in your .env file, and that the target Postgres
database already exists (this script creates tables, not the database
itself).
"""

from backend.app import app
from backend.extensions import db
from backend import models  # noqa: F401  (ensures models are registered)


def main():
    with app.app_context():
        db.create_all()
        print("✅ Database tables created successfully.")


if __name__ == "__main__":
    main()
