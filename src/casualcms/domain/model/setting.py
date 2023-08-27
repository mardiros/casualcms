from datetime import datetime
from typing import Generic

from pydantic import BaseModel, Field

from casualcms.domain.messages import Event
from casualcms.domain.model.abstract_setting import Setting_contra
from casualcms.domain.model.fields import SlugField
from casualcms.utils import generate_id

uuid = str


class PublicMetadata(BaseModel):
    """Metadata exposed to the API"""

    key: str = Field(...)
    hostname: str = Field(...)


class Setting(BaseModel, Generic[Setting_contra]):

    id: uuid = Field(default_factory=generate_id, exclude=True)
    hostname: str = Field(...)
    key: SlugField = Field(...)

    events: list[Event] = Field(default_factory=list, exclude=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, exclude=True)

    setting: Setting_contra = Field(...)

    def __hash__(self) -> int:  # type: ignore
        return hash(self.id)

    @property
    def metadata(self) -> PublicMetadata:
        return PublicMetadata(key=self.key, hostname=self.hostname)
