from datetime import datetime
from typing import Any, Mapping, MutableMapping

from pydantic import Field
from pydantic.fields import ModelField

from casualcms.domain.messages import Event
from casualcms.domain.model.abstract_snippet import AbstractSnippet, SnippetKey
from casualcms.utils import generate_id

uuid = str


class Snippet(AbstractSnippet):

    id: uuid = Field(default_factory=generate_id, exclude=True)
    key: SnippetKey = Field(...)

    events: list[Event] = Field(default_factory=list, exclude=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, exclude=True)

    class Meta:
        abstract = True

    def __hash__(self) -> int:  # type: ignore
        return hash(self.id)

    def get_data_context(self) -> MutableMapping[str, Any]:
        return {
            "meta": {
                "type": self.__meta__.type,
            },
            **self.dict(),
        }

    def get_context(self) -> MutableMapping[str, Any]:
        return self.get_data_context()

    @classmethod
    def ui_schema(cls) -> Mapping[str, Any]:
        ret: dict[str, Any] = {}
        for key, val in cls.__fields__.items():
            if key in ("id", "events", "created_at"):
                continue
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
