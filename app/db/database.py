from sqlalchemy.ext.asyncio import AsyncSession , create_async_engine
from sqlalchemy.orm import sessionmaker ,declarative_base
from app.core.config import settings
from sqlalchemy import Column, Integer, Boolean, DateTime
from datetime import datetime
DATABASE_URL = settings.DATABASE_URL

engine = create_async_engine(DATABASE_URL,echo=True)

async_session = sessionmaker(engine, expire_on_commit=False , class_=AsyncSession)
Base = declarative_base()

# ✅ ADD THIS
class BaseModel(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)