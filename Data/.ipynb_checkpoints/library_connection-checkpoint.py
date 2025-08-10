from sqlalchemy import create_engine

connection_string = "sqlite:///library.db"
engine = create_engine(connection_string)