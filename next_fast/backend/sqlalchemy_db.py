from sqlalchemy import create_engine
from config import DB_USERNAME, DB_PASSWORD, DB_ENDPOINT, DB_NAME
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
SQLALCHEMY_DATABASE_URL = 'mysql+pymysql://' + DB_USERNAME + ':' + DB_PASSWORD + '@' + DB_ENDPOINT + ':3306/' + DB_NAME
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True, poolclass=NullPool)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
    finally:
        db.close()
