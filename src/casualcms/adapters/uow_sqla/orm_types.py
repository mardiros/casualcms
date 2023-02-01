"""SQLAlchemy schema for the supervisor api."""

import json
from typing import Any, Optional, Type

from citext import CIText  # type: ignore
from sqlalchemy import (
    CHAR,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    TypeDecorator,
    event,
)
from sqlalchemy.dialects.postgresql import INET as PgINET
from sqlalchemy.dialects.postgresql import JSONB as PgJSONB
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.engine.interfaces import Dialect
from sqlalchemy.sql.type_api import TypeEngine

setattr(CIText, "cache_ok", True)  # useless SAWarning

__all__ = [
    "event",
    "Boolean",
    "Column",
    "CIText",
    "DateTime",
    "Enum",
    "ForeignKey",
    "Index",
    "Integer",
    "MetaData",
    "String",
    "Table",
    "Text",
    # Defined type
    "UUID",
    "JSON",
    "IpAddress",
]


class UUID(TypeDecorator[String]):
    """Platform-independent UUID type."""

    impl = CHAR
    cache_ok = True

    @property
    def _type_affinity(self) -> Optional[Type[TypeEngine[String]]]:
        return None

    def load_dialect_impl(self, dialect: Dialect) -> TypeEngine[str]:
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PgUUID())  # type: ignore
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value: Optional[String], dialect: Dialect) -> str:
        return str(value)

    def process_result_value(
        self,
        value: Optional[Any],
        dialect: Dialect,
    ) -> Optional[String]:
        return value


class JSON(TypeDecorator[Any]):
    """Platform-independent JSONB type, if not postgress limited query."""

    impl = CHAR
    cache_ok = True

    def __init__(self, as_uuid: bool = False):
        self.as_uuid = as_uuid

    def load_dialect_impl(self, dialect: Dialect) -> Any:
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PgJSONB())
        else:
            return dialect.type_descriptor(Text())

    def process_bind_param(self, value: Optional[Any], dialect: Dialect) -> Any:
        if value is None:
            return value
        elif dialect.name == "postgresql":
            return value  # coverage: ignore
        else:
            return json.dumps(value)

    def process_result_value(
        self,
        value: Optional[Any],
        dialect: Dialect,
    ) -> Optional[Any]:
        if value is None:
            return value
        elif dialect.name == "postgresql":
            return value  # coverage: ignore
        else:
            return json.loads(value)


class IpAddress(TypeDecorator[String]):

    impl = CHAR
    cache_ok = True

    # bind/result is idempotent for this type
    cache_ok = True

    def load_dialect_impl(self, dialect: Dialect) -> Any:
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PgINET())
        else:
            return dialect.type_descriptor(String(45))

    def process_bind_param(self, value: Optional[String], dialect: Dialect) -> Any:
        if value is None:
            return value
        elif dialect.name == "postgresql":
            return str(value)  # coverage: ignore
        return value

    def process_result_value(
        self,
        value: Optional[Any],
        dialect: Dialect,
    ) -> Optional[String]:
        return value
