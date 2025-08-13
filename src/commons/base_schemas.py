from datetime import datetime

from pydantic import BaseModel, ConfigDict


class Base(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )


class BaseSchemaMixin(Base):
    pass


class BaseSchemaOut(Base):
    id: int
    created_at: datetime
    updated_at: datetime
