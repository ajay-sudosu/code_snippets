from sqlalchemy import create_engine
from config import DB_USERNAME, DB_PASSWORD, DB_ENDPOINT, DB_NAME
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from sqlalchemy.ext.declarative import declarative_base


SQLALCHEMY_DATABASE_URL = 'mysql+pymysql://' + DB_USERNAME + ':' + DB_PASSWORD + '@' + DB_ENDPOINT + ':3306/' + DB_NAME
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True, poolclass=QueuePool, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency
def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
    finally:
        db.close()
