from typing import Any, Mapping, Set, Type, TypeVar, cast

from pydantic import BaseModel, Field
from pydantic.fields import ModelField
from pydantic.main import ModelMetaclass

uuid = str
SettingType = Type["AbstractSetting"]


class UnregisterType(Exception):
    def __init__(self, typ: str) -> None:
        super().__init__(f"Unregistered type {typ}")


class SettingTypeList:
    _types: dict[str, SettingType] = {}

    def register(self, typ: SettingType) -> None:
        self._types[typ.__meta__.key] = typ

    def resolve_type(self, typ: str) -> SettingType:
        try:
            return self._types[typ]
        except KeyError:
            raise UnregisterType(typ)

    @property
    def types(self) -> Set[SettingType]:
        return set(self._types.values())


def list_setting_types() -> Set[SettingType]:
    return SettingTypeList().types


def resolve_setting_type(key: str) -> SettingType:
    return SettingTypeList().resolve_type(key)


class MissingMetaSettingError(Exception):
    ...


class AbstractSettingError(Exception):
    ...


class SettingMeta(BaseModel):
    abstract: bool = Field(...)
    key: str = Field(...)


class SettingMetaclass(ModelMetaclass):
    def __new__(mcls, name, bases, namespace, **kwargs):  # type: ignore
        new_namespace = {**namespace}
        setting_meta = None
        if "Meta" in namespace:
            meta = cast(object, namespace.pop("Meta"))
            setting_meta = SettingMeta(
                abstract=getattr(meta, "abstract", False),
                key=getattr(meta, "key", f"{namespace['__module__']}:{name}"),
            )
            new_namespace["__meta__"] = setting_meta
        else:
            raise MissingMetaSettingError(
                f"Meta class is missing for setting {namespace['__module__']}:{name}"
            )
        ret = super().__new__(mcls, name, bases, new_namespace, **kwargs)
        if setting_meta and not setting_meta.abstract:
            SettingTypeList().register(ret)  # type: ignore
        return ret


class AbstractSetting(BaseModel, metaclass=SettingMetaclass):
    __meta__: SettingMeta

    class Meta:
        abstract = True

    def __init__(self, **kwargs: Any) -> None:  # type: ignore
        if self.__meta__.abstract is True:
            raise AbstractSettingError(f"Setting {self.__class__.__name__} is abstract")
        super().__init__(**kwargs)

    @classmethod
    def ui_schema(cls) -> Mapping[str, Any]:
        ret: dict[str, Any] = {}
        for key, val in cls.__fields__.items():
            ret[key] = cls.get_widget(val)
        return ret

    @classmethod
    def get_widget(cls, field: ModelField) -> Mapping[str, Any]:

        if "widget" in field.field_info.extra:
            widget = {"ui:widget": field.field_info.extra["widget"]}
            if field.field_info.extra["widget"] != "hidden":
                widget["ui:placeholder"] = field.field_info.extra.get(
                    "placeholder", field.name
                )
            return widget

        if field.is_complex():

            if isinstance(field.get_default(), list):
                items = {}
                for key, val in field.type_.__fields__.items():
                    items[key] = cls.get_widget(val)
                ret: Mapping[str, Any] = {"items": items}
                return ret

        return {
            "ui:widget": {bool: "checkbox"}.get(field.type_, "text"),
            "ui:placeholder": field.field_info.extra.get("placeholder", field.name),
        }


Setting_contra = TypeVar("Setting_contra", bound=AbstractSetting, contravariant=True)