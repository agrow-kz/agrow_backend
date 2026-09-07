from contextlib import asynccontextmanager

from fastapi import FastAPI
from scalar_fastapi import Layout, Theme, get_scalar_api_reference
from starlette.middleware.cors import CORSMiddleware

from src.configuration.dependencies.container import ApplicationContainer
from src.configuration.exception_handlers import setup_exception_handlers
from src.configuration.logging import setup_logger
from src.core.admin.presentation.router import admin_router
from src.core.catalog.presentation.routers.catalog import catalog_router
from src.core.customer.presentation.routers import customer_router
from src.core.iam.presentation.routers import iam
from src.core.listing.presentation.routers import listing_router
from src.core.media.presentation.routers import media_router
from src.core.references.presentation.routers.reference import reference_router
from src.core.vendor.presentation.router import vendor_router


class ApplicationFactory:
    def __init__(self):
        self.container = ApplicationContainer()
        self.settings = self.container.configurations.configuration
        self._configure_logging()
        self.container.gateways.sentry.init()

        self.app = FastAPI(
            title="Sievers Market",
            version="1.0.0",
            lifespan=self._lifespan(),
        )

        setup_exception_handlers(self.app)

    def _configure_logging(self):
        setup_logger(mode=self.settings.mode)

    def _lifespan(self):
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            await self.container.init_resources()
            self.container.gateways.bloom_filter()

            yield
            await self.container.shutdown_resources()

        return lifespan

    def _wire_dependency(self):
        self.container.wire(
            modules=[
                "src.core.iam.presentation.routers",
                "src.core.customer.presentation.routers",
                "src.core.vendor.presentation.router",
                "src.core.shared.presentation.security",
                "src.core.media.presentation.routers",
                "src.core.listing.presentation.routers",
                "src.core.admin.presentation.router",
            ],
            packages=[
                "src.core.catalog.presentation.routers",
                "src.core.references.presentation.routers",
            ],
        )

        self.app.container = self.container
        self.app.state.mode = self.settings.mode()

    def _include_routers(self):
        routers = [
            iam,
            customer_router,
            vendor_router,
            reference_router,
            catalog_router,
            listing_router,
            media_router,
            admin_router,
        ]
        for router in routers:
            self.app.include_router(router)

    def _setup_docs(self):
        @self.app.get("/scalar", include_in_schema=False)
        async def scalar_html():
            return get_scalar_api_reference(
                openapi_url=self.app.openapi_url,
                title=self.app.title,
                theme=Theme.MARS,
                layout=Layout.MODERN,
            )

    def _setup_cors(self):
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.settings.cors_origins(),
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def build(self) -> FastAPI:
        self._wire_dependency()
        self._include_routers()
        self._setup_docs()
        self._setup_cors()
        return self.app


fastapi_app = ApplicationFactory().build()
