from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,DeclarativeBase

URL_BASE_DE_DONNEES = "sqlite:///./fintrack.db"
engine = create_engine(
    URL_BASE_DE_DONNEES,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)
class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()