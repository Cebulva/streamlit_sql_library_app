# library_connection.py
import os
from sqlalchemy import create_engine

# Absolute path to the SQLite database file
DB_PATH = os.path.join(os.path.dirname(__file__), "library.db")

# SQLAlchemy engine for SQLite database, echo=False for production
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False, future=True)
