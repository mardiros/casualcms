from types import UnionType
from typing import Any, Mapping, MutableMapping

from pydantic import BaseModel
from pydantic.fields import ModelField


class BaseUIModel(BaseModel):
    @classmethod
    def ui_schema(cls) -> Mapping[str, Any]:
        ret: dict[str, Any] = {}
        for key, val in cls.__fields__.items():
            if key in (
                "parent",
                "site",
            ):
                continue
            ret[key] = cls.get_widget(val)
        return ret

    @classmethod
    def get_widget(cls, field: ModelField) -> Mapping[str, Any]:

        xtra = field.field_info.extra
        if "widget" in xtra:
            widget = {
                "ui:widget": xtra["widget"],
            }
            if xtra["widget"] != "hidden":
                widget["ui:placeholder"] = xtra.get("placeholder", field.name)
            if xtra["widget"] == "richtext" and "features" in xtra:
                widget["ui:options"] = {"features": xtra["features"]}
            return widget

        if field.is_complex():
            if isinstance(field.get_default(), list):
                items = {}
                if isinstance(field.type_, UnionType):
                    for type_ in field.type_.__args__:
                        for key, val in type_.__fields__.items():
                            items[key] = cls.get_widget(val)
                else:
                    for key, val in field.type_.__fields__.items():
                        items[key] = cls.get_widget(val)
                ret: Mapping[str, Any] = {"items": items}
                return ret
            else:
                subtype: MutableMapping[str, Mapping[str, Any]] = {}
                for key, val in field.type_.__fields__.items():
                    subtype[key] = cls.get_widget(val)
                return subtype

        return {
            "ui:widget": {bool: "checkbox"}.get(field.type_, "text"),
            "ui:placeholder": field.field_info.extra.get("placeholder", field.name),
        }
