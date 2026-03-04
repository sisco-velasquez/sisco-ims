import os
from sqlmodel import SQLModel, create_engine,Session
from dotenv import load_dotenv

load_dotenv()

engine=create_engine(os.getenv("DATABASE_URL"), echo=True)


def get_session():
    with Session(engine) as session:
     yield session

def init_db():
    SQLModel.metadata.create_all(engine)