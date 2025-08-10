import os
from sqlalchemy import create_engine

# Determine location relative to this file
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(PROJECT_ROOT, "library.db")

engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)