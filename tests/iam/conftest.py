import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio

from src.core.iam.domain.entities import Account
from src.core.iam.domain.enums import TokenType
from src.core.iam.domain.value_objects import Email, Password
from src.core.iam.presentation.dto import CreateAccountRequest
from src.core.shared.infrastructure.services.arq_service import ArqService


def create_domain_account(
    is_active: bool | None = False, tokens: list | None = None
) -> Account:
    return Account(
        id=uuid.uuid4(),
        email=Email("test@example.com"),
        password=Password("$2b$12$fakehashstring..."),
        password_changed_at=datetime.now(timezone.utc),
        is_active=is_active,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        tokens=tokens if tokens is not None else [],
    )


def create_user_request() -> CreateAccountRequest:
    return CreateAccountRequest(
        email="test@example.com",
        raw_password="super_secret",
    )


@pytest.fixture
def mock_arq(container):
    mock = AsyncMock(spec=ArqService)
    container.shared.arq_service.override(mock)
    return mock


def get_token_by_type(tokens: list, target_type: TokenType):
    return next((t for t in tokens if t.type == target_type), None)


def get_token_by_value(tokens: list, target_value: str):
    return next((t for t in tokens if t.value == target_value), None)


@pytest.fixture
def password_service(container):
    return container.iam.password_service()


@pytest_asyncio.fixture
async def token_service(container):
    return container.iam.pyjwt_token_service()


@pytest.fixture
def create_user_usecase(container, mock_arq):
    return container.iam.create_account_usecase()


@pytest.fixture
def account_confirmation_usecase(container):
    return container.iam.account_confirmation_usecase()


@pytest.fixture
def resend_confirmation_code_usecase(container, mock_arq):
    return container.iam.resend_confirmation_code_usecase()


@pytest.fixture
def login_user_usecase(container):
    return container.iam.login_user_usecase()


@pytest.fixture
def logout_user_usecase(container):
    return container.iam.logout_user_usecase()


@pytest.fixture
def refresh_token_usecase(container):
    return container.iam.refresh_token_usecase()


@pytest.fixture
def forgot_password_usecase(container, mock_arq):
    return container.iam.forgot_password_usecase()


@pytest.fixture
def reset_password_usecase(container):
    return container.iam.reset_password_usecase()


@pytest.fixture
def change_password_usecase(container):
    return container.iam.change_password_usecase()


@pytest.fixture
async def account_repository(container):
    return await container.iam.account_repository()


@pytest.fixture
def redis_service(container):
    return container.shared.redis_service()
