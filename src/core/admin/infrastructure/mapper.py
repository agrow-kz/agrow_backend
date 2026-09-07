from src.core.admin.domain.entities import Admin as DomainAdmin
from src.core.admin.domain.entities import Permission
from src.core.admin.infrastructure.models import Admin as ORMAdmin


class AdminMapper:
    @staticmethod
    def to_domain(orm: ORMAdmin) -> DomainAdmin:
        domain_permissions = [
            Permission(
                id=p.id,
                code=p.codename,
                description=p.description or "",
            )
            for p in orm.permissions
        ]

        return DomainAdmin(
            id=orm.id,
            account_id=orm.account_id,
            last_name=orm.last_name,
            first_name=orm.first_name,
            patronymic=orm.patronymic or "",
            role=orm.role,
            permissions=domain_permissions,
        )

    @staticmethod
    def to_orm(domain: DomainAdmin) -> ORMAdmin:
        return ORMAdmin(
            id=domain.id,
            account_id=domain.account_id,
            last_name=domain.last_name,
            first_name=domain.first_name,
            patronymic=domain.patronymic,
            role=domain.role,
        )
