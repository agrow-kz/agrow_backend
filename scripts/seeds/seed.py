import logging
from pathlib import Path
from typing import Any
from uuid import UUID

import yaml
from dotenv import load_dotenv
from pydantic import TypeAdapter
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from scripts.seeds.schemas import (
    AttributeDefinitionSeed,
    AttributeGroupSeed,
    BrandSeed,
    ColorSeed,
    CountrySeed,
    PermissionSeed,
    RegionSeed,
    RubricSeed,
    SubcategoryAttributesSeed,
    UnitSeed,
)
from src.configuration.settings.settings import PostgresSettings
from src.core.admin.infrastructure.models import Permission
from src.core.catalog.infrastructure.enums import AttributeType, CatalogStatus
from src.core.catalog.infrastructure.models import (
    AttributeDefinition,
    AttributeGroup,
    Category,
    Rubric,
    Subcategory,
    SubcategoryAttribute,
    UnitOfMeasure,
)
from src.core.references.infrastructure.models import (
    Brand,
    City,
    Color,
    Country,
    Region,
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"

if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
    print(f"✅ .env loaded from {ENV_PATH}")
else:
    print(f"❌ .env NOT FOUND at {ENV_PATH}")

logger = logging.getLogger(__name__)


class DataSeeder:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.data_dir = Path(__file__).resolve().parent / "data"

    def _load_yaml(self, file_name: str) -> Any:
        file_path = self.data_dir / file_name
        if not file_path.exists():
            logger.error(f"❌ File not found: {file_path}")
            return None
        with open(file_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    async def seed_brands(self):
        raw_data = self._load_yaml("references/brands.yaml")
        if not raw_data:
            return
        brands = TypeAdapter(list[BrandSeed]).validate_python(raw_data)
        for dto in brands:
            self.session.add(Brand(name=dto.name))
        logger.info("✅ Brands seeded")

    async def seed_colors(self):
        raw_data = self._load_yaml("references/colors.yaml")
        if not raw_data:
            return
        colors = TypeAdapter(list[ColorSeed]).validate_python(raw_data)
        for dto in colors:
            self.session.add(Color(name=dto.name, hex=dto.hex))
        logger.info("✅ Colors seeded")

    async def seed_countries(self):
        raw_data = self._load_yaml("references/countries.yaml")
        if not raw_data:
            return
        countries = TypeAdapter(list[CountrySeed]).validate_python(raw_data)
        for dto in countries:
            self.session.add(Country(name=dto.name))
        logger.info("✅ Countries seeded")

    async def seed_locations(self):
        raw_data = self._load_yaml("references/locations.yaml")
        if not raw_data:
            return
        regions = TypeAdapter(list[RegionSeed]).validate_python(raw_data)
        for r_dto in regions:
            region = Region(name=r_dto.name)
            self.session.add(region)
            await self.session.flush()
            for city_name in r_dto.cities:
                self.session.add(City(name=city_name, region_id=region.id))
        logger.info("✅ Regions and Cities seeded")

    async def seed_attribute_groups(self) -> dict[str, UUID]:
        raw_data = self._load_yaml("attributes/groups.yaml")
        groups = TypeAdapter(list[AttributeGroupSeed]).validate_python(raw_data or [])

        key_to_id = {}
        for dto in groups:
            group = AttributeGroup(key=dto.key, label=dto.label, position=dto.position)
            self.session.add(group)
            await self.session.flush()
            key_to_id[dto.key] = group.id

        logger.info("✅ Attribute groups seeded")
        return key_to_id

    async def seed_units(self) -> dict[str, UUID]:
        raw_data = self._load_yaml("attributes/units.yaml")
        units = TypeAdapter(list[UnitSeed]).validate_python(raw_data or [])

        key_to_id = {}
        for dto in units:
            unit = UnitOfMeasure(key=dto.key, label=dto.label)
            self.session.add(unit)
            await self.session.flush()
            key_to_id[dto.key] = unit.id

        logger.info("✅ Units of measure seeded")
        return key_to_id

    async def seed_attribute_definitions(self) -> dict[str, UUID]:
        raw_data = self._load_yaml("attributes/definitions.yaml")
        definitions = TypeAdapter(list[AttributeDefinitionSeed]).validate_python(
            raw_data or []
        )

        key_to_id = {}
        for dto in definitions:
            definition = AttributeDefinition(
                key=dto.key,
                label=dto.label,
                type=AttributeType(dto.type),
                options=[opt.model_dump() for opt in dto.options],
                source=dto.source,
            )
            self.session.add(definition)
            await self.session.flush()
            key_to_id[dto.key] = definition.id

        logger.info("✅ Attribute definitions seeded")
        return key_to_id

    async def seed_catalog_hierarchy(self) -> dict[str, UUID]:
        raw_data = self._load_yaml("categories/categories.yaml")
        rubrics = TypeAdapter(list[RubricSeed]).validate_python(raw_data or [])

        subcategory_name_to_id = {}
        for r_dto in rubrics:
            rubric = Rubric(name=r_dto.name, status=CatalogStatus.ACTIVE)
            self.session.add(rubric)
            await self.session.flush()

            for c_dto in r_dto.categories:
                category = Category(
                    rubric_id=rubric.id, name=c_dto.name, status=CatalogStatus.ACTIVE
                )
                self.session.add(category)
                await self.session.flush()

                for s_dto in c_dto.subcategories:
                    subcategory = Subcategory(
                        category_id=category.id,
                        name=s_dto.name,
                        status=CatalogStatus.ACTIVE,
                    )
                    self.session.add(subcategory)
                    await self.session.flush()
                    subcategory_name_to_id[s_dto.name] = subcategory.id

        logger.info("✅ Catalog hierarchy seeded")
        return subcategory_name_to_id

    async def seed_subcategory_attributes(
        self,
        subcategory_name_to_id: dict[str, UUID],
        attribute_key_to_id: dict[str, UUID],
        group_key_to_id: dict[str, UUID],
        unit_key_to_id: dict[str, UUID],
    ):
        raw_data = self._load_yaml("attributes/links.yaml")
        links_data = TypeAdapter(list[SubcategoryAttributesSeed]).validate_python(
            raw_data or []
        )

        for entry in links_data:
            subcategory_id = subcategory_name_to_id.get(entry.subcategory)
            if not subcategory_id:
                logger.error(
                    f"❌ Subcategory not found for attributes seed: {entry.subcategory}"
                )
                continue

            for link_dto in entry.attributes:
                attribute_id = attribute_key_to_id.get(link_dto.attribute)
                group_id = group_key_to_id.get(link_dto.group)
                unit_id = unit_key_to_id.get(link_dto.unit) if link_dto.unit else None

                if not attribute_id or not group_id:
                    logger.error(
                        f"Skipping link: attribute={link_dto.attribute} "
                        f"group={link_dto.group} "
                        f"not found for subcategory={entry.subcategory}"
                    )
                    continue

                self.session.add(
                    SubcategoryAttribute(
                        subcategory_id=subcategory_id,
                        attribute_id=attribute_id,
                        group_id=group_id,
                        unit_id=unit_id,
                        required=link_dto.required,
                        filterable=link_dto.filterable,
                        position=link_dto.position,
                    )
                )

        logger.info("✅ Subcategory attributes linked")

    async def seed_permissions(self):
        raw_data = self._load_yaml("permissions/permissions.yaml")
        if not raw_data:
            return
        permissions = TypeAdapter(list[PermissionSeed]).validate_python(raw_data)
        for dto in permissions:
            self.session.add(Permission(codename=dto.codename))
        logger.info("✅ Permissions seeded")

    async def is_already_seeded(self) -> bool:
        result = await self.session.execute(select(func.count()).select_from(Rubric))
        return result.scalar_one() > 0

    async def seed_all(self):
        if await self.is_already_seeded():
            print("⏭️ Database already seeded, skipping")
            return

        try:
            await self.seed_brands()
            await self.seed_colors()
            await self.seed_countries()
            await self.seed_locations()
            await self.seed_permissions()

            group_key_to_id = await self.seed_attribute_groups()
            unit_key_to_id = await self.seed_units()
            attribute_key_to_id = await self.seed_attribute_definitions()
            subcategory_name_to_id = await self.seed_catalog_hierarchy()

            await self.seed_subcategory_attributes(
                subcategory_name_to_id=subcategory_name_to_id,
                attribute_key_to_id=attribute_key_to_id,
                group_key_to_id=group_key_to_id,
                unit_key_to_id=unit_key_to_id,
            )

            await self.session.commit()
            logger.info("🚀 All data seeded successfully!")
        except Exception as e:
            await self.session.rollback()
            logger.error(f"❌ Seeding failed: {e}")
            raise


async def main():
    db_settings = PostgresSettings()
    engine = create_async_engine(url=db_settings.database_url, echo=False)
    session_factory = async_sessionmaker(
        bind=engine, autoflush=False, expire_on_commit=False
    )

    async with session_factory() as session:
        seeder = DataSeeder(session)
        await seeder.seed_all()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
