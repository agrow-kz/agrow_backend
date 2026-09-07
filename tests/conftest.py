from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from loguru import logger
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from scripts.seeds.seed import DataSeeder
from src.configuration.database.connection import Base
from src.configuration.dependencies.container import ApplicationContainer
from src.configuration.settings.settings import ApplicationSettings
from src.core.shared.infrastructure.services.meilisearch_service import (
    MeilisearchService,
)

pytest_plugins = [
    "tests.iam.conftest",
    "tests.customer.conftest",
    "tests.vendor.conftest",
    "tests.listing.conftest",
    "tests.catalog.conftest",
]


@pytest.fixture(scope="session")
def test_settings() -> ApplicationSettings:
    return ApplicationSettings()


@pytest_asyncio.fixture(scope="session")
async def test_engine(test_settings: ApplicationSettings):
    if test_settings.mode != "test":
        pytest.exit(
            f"СТОП! Попытка запустить тесты на рабочей БД: {test_settings.database.name}"  # noqa: E501
        )

    async_engine = create_async_engine(
        url=test_settings.database.database_url, echo=False, poolclass=NullPool
    )

    yield async_engine
    await async_engine.dispose()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database(test_engine):
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(
        bind=test_engine, expire_on_commit=False, class_=AsyncSession
    )
    async with async_session() as session:
        seeder = DataSeeder(session=session)
        await seeder.seed_all()

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def session_factory(test_engine):
    async with test_engine.connect() as conn:
        transaction = await conn.begin()
        await conn.begin_nested()

        factory = async_sessionmaker(
            bind=conn,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            join_transaction_mode="create_savepoint",
        )

        yield factory
        await transaction.rollback()


@pytest_asyncio.fixture
async def database_session(session_factory):
    async with session_factory() as session:
        yield session


@pytest.fixture(scope="function")
def mock_bloom():
    bloom = MagicMock()
    bloom.__contains__ = MagicMock(return_value=False)
    return bloom


@pytest.fixture(scope="session", autouse=True)
def mute_logger():
    logger.remove()
    yield


@pytest.fixture(autouse=True)
def mock_search_service(container):
    mock = AsyncMock(spec=MeilisearchService)
    with container.shared.meilisearch_service.override(mock):
        yield mock


@pytest_asyncio.fixture(scope="function")
async def container(session_factory, test_settings, mock_bloom):
    container = ApplicationContainer()
    container.configurations.configuration.from_pydantic(test_settings)
    container.gateways.session_factory.override(session_factory)
    container.gateways.bloom_filter.override(mock_bloom)

    yield container
