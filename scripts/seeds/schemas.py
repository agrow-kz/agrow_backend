from src.core.shared.presentation.dto import DTO


class OptionSeed(DTO):
    key: str
    label: str


class AttributeDefinitionSeed(DTO):
    key: str
    label: str
    type: str
    options: list[OptionSeed] = []
    source: str | None = None


class AttributeGroupSeed(DTO):
    key: str
    label: str
    position: int = 0


class UnitSeed(DTO):
    key: str
    label: str


class SubcategorySeed(DTO):
    name: str


class CategorySeed(DTO):
    name: str
    subcategories: list[SubcategorySeed]


class RubricSeed(DTO):
    name: str
    categories: list[CategorySeed]


class SubcategoryAttributeLinkSeed(DTO):
    attribute: str
    group: str
    unit: str | None = None
    required: bool = False
    filterable: bool = False
    position: int = 0


class SubcategoryAttributesSeed(DTO):
    subcategory: str
    attributes: list[SubcategoryAttributeLinkSeed]


class BrandSeed(DTO):
    name: str


class ColorSeed(DTO):
    name: str
    hex: str


class RegionSeed(DTO):
    name: str
    cities: list[str]


class CountrySeed(DTO):
    name: str


class PermissionSeed(DTO):
    codename: str
    description: str | None = None
