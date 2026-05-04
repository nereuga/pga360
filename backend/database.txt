from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Carrega a URL do banco do ambiente (Docker Net)
# Ex: postgresql://user:password@db-360:5432/pga_360_db
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# O pool_pre_ping ajuda a manter a conexão viva em ambientes de rede instáveis
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Gerenciador de Sessão para os Endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()