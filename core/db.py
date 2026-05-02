from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()


def get_engine():
    from core.settings import settings
    logger.info(f"Conectando ao banco: {settings.db_host}:{settings.db_port}/{settings.db_name}")
    return create_engine(
        settings.database_url,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )


def get_session():
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()


def create_all_tables():
    """Cria todas as tabelas mapeadas nos models (roda no init do container)."""
    from core import models  # noqa: F401
    engine = get_engine()
    Base.metadata.create_all(engine)
    logger.info("Tabelas criadas/verificadas com sucesso.")