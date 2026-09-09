from datetime import datetime, timedelta, timezone

import pytest

from src.core.iam.domain.enums import TokenType
from src.core.iam.domain.exceptions import (
    AccountAlreadyConfirmedError,
    AccountNotConfirmedError,
)
from src.core.iam.domain.value_objects import HashedPassword
from tests.iam.conftest import (
    create_domain_account,
    get_token_by_type,
    get_token_by_value,
)


@pytest.mark.unit
def test_confirm_account_success():
    account = create_domain_account(is_active=False)
    account.confirm_account()
    assert account.is_active is True


@pytest.mark.unit
def test_confirm_account_fails_when_already_active():
    account = create_domain_account(is_active=True)
    with pytest.raises(AccountAlreadyConfirmedError):
        account.confirm_account()


@pytest.mark.unit
def test_login_success():
    account = create_domain_account(is_active=True)
    account.password = HashedPassword(value="hashed_password")
    account.login()


@pytest.mark.unit
def test_login_fails_when_user_inactive():
    account = create_domain_account(is_active=False)
    with pytest.raises(AccountNotConfirmedError):
        account.login()


@pytest.mark.unit
def test_change_password_success():
    account = create_domain_account(is_active=True)
    account.password = HashedPassword(value="old_hashed_password")

    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    account.add_new_token(TokenType.REFRESH, "refresh_token_123", expires_at)

    account.change_password(HashedPassword("new_hashed_password"))

    assert account.password.value == "new_hashed_password"
    refresh_token = get_token_by_type(account.tokens, TokenType.REFRESH)
    assert refresh_token.is_revoked is True


@pytest.mark.unit
def test_logout_success():
    account = create_domain_account(is_active=True)
    token_value = "valid_access_token"
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    account.add_new_token(TokenType.ACCESS, token_value, expires_at)

    account.logout(token_value)

    token = get_token_by_value(account.tokens, token_value)
    assert token.is_revoked is True


@pytest.mark.unit
def test_rotate_refresh_token_success():
    account = create_domain_account(is_active=True)
    old_token_value = "old_refresh_token"
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    account.add_new_token(TokenType.REFRESH, old_token_value, expires_at)

    new_token_value = "new_refresh_token"
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    account.rotate_refresh_token(old_token_value, new_token_value, expires_at)

    old_refresh_token = get_token_by_value(account.tokens, old_token_value)
    new_refresh_token = get_token_by_value(account.tokens, new_token_value)

    assert old_refresh_token.is_revoked is True
    assert new_refresh_token.is_revoked is False


@pytest.mark.unit
def test_reset_password_success():
    account = create_domain_account(is_active=True)

    fake_refresh_token = "refresh_token_1"
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    account.add_new_token(TokenType.REFRESH, fake_refresh_token, expires_at)

    new_hashed_password = "new_hashed_password"
    account.reset_password(new_hashed_password)

    revoked_refresh_tokens = [
        token for token in account.tokens if token.type == TokenType.REFRESH
    ]
    for token in revoked_refresh_tokens:
        assert token.is_revoked is True
