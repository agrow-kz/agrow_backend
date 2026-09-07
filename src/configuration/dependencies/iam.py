from datetime import timedelta

from dependency_injector import containers, providers

from src.core.iam.application.services.otp import OTPService
from src.core.iam.application.usecases import (
    AccountConfirmationUseCase,
    ChangePasswordUseCase,
    ConfirmEmailChangeUseCase,
    CreateAccountUseCase,
    ForgotPasswordUseCase,
    LoginUserUseCase,
    LogoutUserUseCase,
    RefreshTokenUseCase,
    RequestEmailChangeUseCase,
    ResendConfirmationCodeUseCase,
    ResetPasswordUseCase,
)
from src.core.iam.infrastructure.repository import AccountRepository
from src.core.iam.infrastructure.services.password_service import PasswordService
from src.core.iam.infrastructure.services.pyjwt_token import PyJWTTokenService
from src.core.iam.infrastructure.services.query_service import GetMeQueryService
from src.core.iam.infrastructure.uow import IAMUnitOfWork
from src.core.shared.infrastructure.services.phone_normalizer import PhoneNormalizer


class IAMContainer(containers.DeclarativeContainer):
    auth_config = providers.Configuration()
    session_factory = providers.Dependency()
    database_session = providers.Dependency()
    console_email_sender = providers.Dependency()
    redis_service = providers.Dependency()
    arq_service = providers.Dependency()
    bloom_filter = providers.Dependency()

    query_service = providers.Factory(GetMeQueryService, session=database_session)

    password_service = providers.Factory(
        PasswordService,
        bloom=bloom_filter,
    )

    account_repository = providers.Factory(AccountRepository, session=database_session)

    uow = providers.Factory(IAMUnitOfWork, session_factory=session_factory)

    phonenumber_normalizer = providers.Singleton(PhoneNormalizer)

    pyjwt_token_service = providers.Singleton(
        PyJWTTokenService,
        secret_key=auth_config.secret_key,
        algorithm=auth_config.algorithm,
        access_token_lifetime=providers.Factory(
            timedelta, minutes=auth_config.access_token_lifetime.as_int()
        ),
        refresh_token_lifetime=providers.Factory(
            timedelta, days=auth_config.refresh_token_lifetime.as_int()
        ),
    )

    otp_service = providers.Factory(
        OTPService,
        cache=redis_service,
        queue=arq_service,
    )

    create_account_usecase = providers.Factory(
        CreateAccountUseCase,
        uow=uow,
        otp_service=otp_service,
        password_service=password_service,
    )

    account_confirmation_usecase = providers.Factory(
        AccountConfirmationUseCase,
        uow=uow,
        otp_service=otp_service,
        token_service=pyjwt_token_service,
    )

    resend_confirmation_code_usecase = providers.Factory(
        ResendConfirmationCodeUseCase,
        uow=uow,
        otp_service=otp_service,
    )

    login_user_usecase = providers.Factory(
        LoginUserUseCase,
        uow=uow,
        token_service=pyjwt_token_service,
        password_service=password_service,
    )

    refresh_token_usecase = providers.Factory(
        RefreshTokenUseCase,
        uow=uow,
        token_service=pyjwt_token_service,
    )

    logout_user_usecase = providers.Factory(
        LogoutUserUseCase,
        uow=uow,
    )

    forgot_password_usecase = providers.Factory(
        ForgotPasswordUseCase,
        uow=uow,
        otp_service=otp_service,
    )

    reset_password_usecase = providers.Factory(
        ResetPasswordUseCase,
        uow=uow,
        password_service=password_service,
        otp_service=otp_service,
    )

    change_password_usecase = providers.Factory(
        ChangePasswordUseCase,
        uow=uow,
        password_service=password_service,
    )

    request_email_change_usecase = providers.Factory(
        RequestEmailChangeUseCase,
        uow=uow,
        otp_service=otp_service,
        cache_service=redis_service,
    )

    confirm_email_change_usecase = providers.Factory(
        ConfirmEmailChangeUseCase,
        uow=uow,
        otp_service=otp_service,
        cache_service=redis_service,
    )
