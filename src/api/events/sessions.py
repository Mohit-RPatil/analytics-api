import sqlmodel
from sqlmodel import SQLModel, Session
import timescaledb
from .db.config import DATABASE_URL, DB_TIMEZONE

if DATABASE_URL == "":
    raise NotImplementedError("Database_URL need to be set")

import os
from dotenv import load_dotenv

# Determine environment
ENV = os.getenv("ENV", "local")

# Load correct .env file
if ENV == "docker":
    load_dotenv(".env.compose")
else:
    load_dotenv(".env")

print("Running environment:", ENV)
print("Using DB:", os.getenv("DATABASE_URL"))

engine = timescaledb.create_engine(DATABASE_URL, timezone=DB_TIMEZONE)


def init_db():
    print("creating database") 
    SQLModel.metadata.create_all(engine)
    print("Creating Hypertables")
    timescaledb.metadata.create_all(engine)

def get_session():
    with Session(engine) as session: 
        yield session