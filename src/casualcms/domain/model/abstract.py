from types import GenericAlias, UnionType
from typing import Any, Mapping, cast

from pydantic import BaseModel
from pydantic.fields import FieldInfo


class BaseUIModel(BaseModel):
    @classmethod
    def ui_schema(cls) -> Mapping[str, Any]:
        ret: dict[str, Any] = {}
        for key, val in cls.model_fields.items():
            if key in (
                "parent",
                "site",
            ):
                continue
            ret[key] = cls.get_widget(key, val)
        return ret

    @classmethod
    def get_widget(cls, name: str, field: FieldInfo) -> Mapping[str, Any]:
        xtra = cast(dict[str, Any], field.json_schema_extra or {})
        if "widget" in xtra:
            widget = {
                "ui:widget": xtra["widget"],
            }
            if xtra["widget"] != "hidden":
                widget["ui:placeholder"] = xtra.get("placeholder", name)
            if xtra["widget"] == "richtext" and "features" in xtra:
                widget["ui:options"] = {"features": xtra["features"]}
            return widget

        field_type = field.annotation
        if isinstance(field_type, (UnionType, GenericAlias)):
            if isinstance(field_type, GenericAlias):

                field_type_ = field_type.__args__[0]  # type: ignore
                items = {}
                if isinstance(field_type_, UnionType):
                    for type_ in field_type_.__args__:
                        for key, val in type_.model_fields.items():
                            items[key] = cls.get_widget(key, val)
                else:
                    for key, val in field_type_.model_fields.items():  # type: ignore
                        items[key] = cls.get_widget(key, val)  # type: ignore
                ret: Mapping[str, Any] = {"items": items}
                return ret
            else:
                subtype = {}
                for type_ in field_type_.__args__:  # type: ignore
                    for key, val in type_.model_fields.items():  # type: ignore
                        subtype[key] = cls.get_widget(key, val)  # type: ignore
                ret: Mapping[str, Any] = {"items": subtype}
                return ret

        return {
            "ui:widget": {bool: "checkbox"}.get(field_type, "text"),  # type: ignore
            "ui:placeholder": xtra.get("placeholder", field.title or name),
        }
