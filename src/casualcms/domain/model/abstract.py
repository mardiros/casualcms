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

        xtra = cast(dict[str, Any], field.json_schema_extra)
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
        # if field.is_complex():
        #     if isinstance(field.get_default(), list):
        #         items = {}
        #         if isinstance(field_type, UnionType):
        #             for type_ in field_type.__args__:
        #                 for key, val in type_.model_fields.items():
        #                     items[key] = cls.get_widget(val)
        #         else:
        #             for key, val in field_type.model_fields.items():
        #                 items[key] = cls.get_widget(val)
        #         ret: Mapping[str, Any] = {"items": items}
        #         return ret
        #     else:
        #         subtype: MutableMapping[str, Mapping[str, Any]] = {}
        #         for key, val in field_type.model_fields.items():
        #             subtype[key] = cls.get_widget(val)
        #         return subtype

        return {
            "ui:widget": {bool: "checkbox"}.get(field_type, "text"),  # type: ignore
            "ui:placeholder": xtra.get("placeholder", field.title),
        }
