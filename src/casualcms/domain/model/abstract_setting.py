import re
from typing import Any, Set, Type, TypeVar, cast

from pydantic import BaseModel, Field
from pydantic.main import ModelMetaclass

from casualcms.domain.exceptions import MissingMetaError
from casualcms.domain.model.abstract import BaseUIModel

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


class AbstractSettingError(Exception):
    ...


class SettingMeta(BaseModel):
    abstract: bool = Field(...)
    key: str = Field(...)
    title: str = Field(...)


class SettingMetaclass(ModelMetaclass):
    def __new__(mcls, name, bases, namespace, **kwargs):  # type: ignore
        new_namespace = {**namespace}
        short_name = f"{namespace['__qualname__']}"
        long_name = f"{namespace['__module__']}:{short_name}"
        setting_meta = None
        if "Meta" in namespace:
            meta = cast(object, namespace.pop("Meta"))
            key = getattr(meta, "key", long_name)
            setting_meta = SettingMeta(
                abstract=getattr(meta, "abstract", False),
                key=key,
                title=getattr(
                    meta,
                    "title",
                    re.sub("([A-Z])", r" \g<0>", short_name).strip(),
                ),
            )
            new_namespace["__meta__"] = setting_meta
        else:
            raise MissingMetaError(long_name)
        ret = super().__new__(  # type: ignore
            mcls, name, bases, new_namespace, **kwargs  # type: ignore
        )
        if setting_meta:
            ret.__config__.title = setting_meta.title  # type: ignore
            if not setting_meta.abstract:
                SettingTypeList().register(ret)  # type: ignore
        return ret  # type: ignore


class AbstractSetting(BaseUIModel, metaclass=SettingMetaclass):
    __meta__: SettingMeta

    class Meta:
        abstract = True

    def __init__(self, **kwargs: Any) -> None:  # type: ignore
        if self.__meta__.abstract is True:
            raise AbstractSettingError(f"Setting {self.__class__.__name__} is abstract")
        super().__init__(**kwargs)


Setting_contra = TypeVar("Setting_contra", bound=AbstractSetting, contravariant=True)
