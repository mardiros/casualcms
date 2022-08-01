"""SQLAlchemy schema for the supervisor api."""

import json
from typing import Any

from citext import CIText  # type: ignore
from sqlalchemy import (  # type: ignore
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
from sqlalchemy.engine.interfaces import Dialect  # type: ignore
from sqlalchemy.sql.type_api import TypeEngine  # type: ignore

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


class UUID(TypeDecorator):
    """Platform-independent UUID type."""

    impl = CHAR
    _type_affinity = None

    def load_dialect_impl(self, dialect: Dialect) -> TypeEngine:
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PgUUID())  # type: ignore
        else:
            return dialect.type_descriptor(CHAR(36))  # type: ignore

    def process_bind_param(  # type: ignore
        self, value: TypeEngine, dialect: Dialect
    ) -> str:
        return str(value)

    def process_result_value(  # type: ignore
        self,
        value: TypeEngine,
        dialect: Dialect,
    ) -> TypeEngine:
        return value


class JSON(TypeDecorator):
    """Platform-independent JSONB type, if not postgress limited query."""

    impl = CHAR

    def __init__(self, as_uuid: bool = False):
        self.as_uuid = as_uuid

    def load_dialect_impl(self, dialect: Dialect) -> Any:  # FIXME: type
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PgJSONB())
        else:
            return dialect.type_descriptor(Text())

    def process_bind_param(self, value: TypeEngine, dialect: Dialect) -> Any:
        if value is None:
            return value
        elif dialect.name == "postgresql":
            return value
        else:
            return json.dumps(value)

    def process_result_value(  # type: ignore
        self,
        value: Any,
        dialect: Dialect,
    ) -> TypeEngine:
        if value is None:
            return value
        elif dialect.name == "postgresql":
            return value
        else:
            return json.loads(value)


class IpAddress(TypeDecorator):

    impl = CHAR

    # bind/result is idempotent for this type
    cache_ok = True

    def load_dialect_impl(self, dialect: Dialect) -> Any:  # FIXME: type
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PgINET())
        else:
            return dialect.type_descriptor(String(45))

    def process_bind_param(self, value: TypeEngine, dialect: Dialect) -> Any:
        if value is None:
            return value
        elif dialect.name == "postgresql":
            return str(value)
        return value

    def process_result_value(  # type: ignore
        self,
        value: Any,
        dialect: Dialect,
    ) -> TypeEngine:
        return value
