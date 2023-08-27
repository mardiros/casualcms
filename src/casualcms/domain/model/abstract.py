from decimal import Decimal
from types import NoneType, UnionType
from typing import Any, Literal, Mapping, Optional, Type, Union, get_origin

from pydantic import BaseModel

UISchema = Mapping[str, Any]


class WidgetFactory:
    def __init__(self, base: "Type[BaseUIModel]"):
        self.base = base

    def get_result(self) -> UISchema:
        return self.build(self.base)

    def build(
        self,
        typ: Any,
        extra: Optional[Mapping[str, Any]] = None,
        field_name: Optional[str] = None,
    ) -> UISchema:

        type_origin = get_origin(typ)
        extra = extra or {}
        if type_origin:
            if type_origin is list:
                return self.build_list(typ, extra, field_name)

            if type_origin is Union or type_origin is UnionType:
                return self.build_union(typ, extra, field_name)

            if type_origin is Literal:
                return self.build_literal(typ, extra, field_name)

        if typ is NoneType:
            return {}

        if issubclass(typ, BaseModel):
            return self.build_model(typ, extra, field_name)

        if issubclass(typ, (bool)):
            return self.build_boolean(typ, extra, field_name)

        if issubclass(typ, (int, str, float, Decimal)):
            return self.build_simpletype(typ, extra, field_name)

        raise NotImplementedError(f"{typ} not implemented")

    def build_model(
        self,
        field_type: Type[BaseModel],
        extra: Mapping[str, Any],
        field_name: Optional[str],
    ) -> UISchema:
        ret: dict[str, Any] = {}
        for key, field in field_type.model_fields.items():
            if field.exclude:
                continue
            extra = {}
            if callable(field.json_schema_extra):
                field.json_schema_extra(extra)
            elif field.json_schema_extra:
                extra.update(field.json_schema_extra)

            ret[key] = self.build(field.annotation, extra, key)
        return ret

    def build_list(
        self, field_type: Any, extra: Mapping[str, Any], field_name: Optional[str]
    ) -> UISchema:
        return {  # there is no extra possible for items
            "items": self.build(field_type.__args__[0]),
            **extra,
        }

    def build_union(
        self, field_type: Any, extra: Mapping[str, Any], field_name: Optional[str]
    ) -> UISchema:
        merged = {**extra}
        for typ in field_type.__args__:
            merged.update(self.build(typ, field_name=field_name))
        return merged  # type: ignore

    def build_boolean(
        self, field_type: Any, extra: Mapping[str, Any], field_name: Optional[str]
    ) -> UISchema:
        return {"ui:widget": "checkbox", "ui:placeholder": field_name, **extra}

    def build_literal(
        self, field_type: Any, extra: Mapping[str, Any], field_name: Optional[str]
    ) -> UISchema:
        return {
            "ui:widget": "select",
            "ui:placeholder": field_name,
            **extra,
        }

    def build_simpletype(
        self, field_type: Any, extra: Mapping[str, Any], field_name: Optional[str]
    ) -> UISchema:
        return {
            "ui:widget": "text",
            "ui:placeholder": field_name,
            **extra,
        }


class BaseUIModel(BaseModel):
    @classmethod
    def ui_schema(cls) -> UISchema:
        return WidgetFactory(cls).get_result()
