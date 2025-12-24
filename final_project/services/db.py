from config import db_config

from sqlalchemy import BigInteger, ForeignKey, Integer, String, Text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


DB_USER = db_config.DB_USER
DB_PASSWORD = db_config.DB_PASSWORD
DB_HOST = db_config.DB_HOST
DB_PORT = db_config.DB_PORT
DB_NAME = db_config.DB_NAME


DATABASE_URL = (
    f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_async_engine(DATABASE_URL, echo=False)

async_session = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession
)


class Base(DeclarativeBase):
    pass


class Walk(Base):
    __tablename__ = "walks"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    date: Mapped[str] = mapped_column(String, nullable=False)
    duration: Mapped[int] = mapped_column(Integer, default=0)
    tasks_count: Mapped[int] = mapped_column(Integer, default=0)
    route: Mapped[str] = mapped_column(Text, nullable=True)

    photos = relationship(
        "Photo",
        back_populates="walk",
        cascade="all, delete-orphan"
    )


class Photo(Base):
    __tablename__ = "photos"

    id: Mapped[int] = mapped_column(primary_key=True)
    walk_id: Mapped[int] = mapped_column(Integer, ForeignKey("walks.id"))
    file_id: Mapped[str] = mapped_column(String(255), nullable=False)

    walk = relationship("Walk", back_populates="photos")


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
