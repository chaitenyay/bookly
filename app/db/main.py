from sqlmodel import create_engine, text, SQLModel
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import Config
from app.loans import models as loan_models  # noqa: F401


engine = AsyncEngine(
    create_engine(Config.DATABASE_URL, echo=True, future=True)
)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session() -> AsyncEngine:

    Session = sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )

    async with Session() as session:
        yield session
    
        
