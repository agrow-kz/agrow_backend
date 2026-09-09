import asyncio
from datetime import datetime, timezone

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from scripts.bloom.load_bloom import load_bloom
from src.configuration.settings.settings import AdminSettings, PostgresSettings
from src.core.admin.domain.enums import AdminRoles
from src.core.admin.infrastructure.models import Admin
from src.core.iam.infrastructure.models import Account
from src.core.iam.infrastructure.services.password_service import PasswordService


async def seed_super_admin():
    db_settings = PostgresSettings()
    admin_settings = AdminSettings()

    engine = create_async_engine(url=db_settings.database_url, echo=False)
    session_factory = async_sessionmaker(
        bind=engine, autoflush=False, expire_on_commit=False
    )

    async with session_factory() as session:
        stmt = select(Account).where(Account.email == admin_settings.super_admin_email)
        result = await session.execute(stmt)
        existing_account = result.scalar_one_or_none()

        if existing_account:
            logger.info("Super Admin account already exists. Skipping")
            return

        bloom_filter = load_bloom()
        password_service = PasswordService(bloom=bloom_filter)

        validated_plain = password_service.validate(admin_settings.super_admin_password)
        hashed_password = password_service.hash(validated_plain)

        account = Account(
            email=admin_settings.super_admin_email,
            password_hash=hashed_password.value,
            is_active=True,
            password_changed_at=datetime.now(timezone.utc),
        )
        session.add(account)
        await session.flush()

        admin = Admin(
            account_id=account.id,
            role=AdminRoles.SUPER_ADMIN,
            last_name=admin_settings.super_admin_last_name,
            first_name=admin_settings.super_admin_first_name,
        )
        session.add(admin)

        await session.commit()
        logger.info("Super Admin successfully created!")


if __name__ == "__main__":
    asyncio.run(seed_super_admin())
