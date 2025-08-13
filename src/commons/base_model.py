from datetime import UTC, datetime

from sqlmodel import TIMESTAMP, Field, SQLModel, text
from pydantic import ConfigDict, field_serializer
from sqlalchemy import func

class BaseModelMixin(SQLModel, table=False):
    id: int = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_type=TIMESTAMP(timezone=True),
        sa_column_kwargs={
            "server_default": text("CURRENT_TIMESTAMP"),
        },
        nullable=False,
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_type=TIMESTAMP(timezone=True),
        sa_column_kwargs={
            "server_default": text("CURRENT_TIMESTAMP"),
            "onupdate": func.now()
        },
        nullable=False,
    )
    deleted: bool = Field(
        default=False,
        nullable=False,
        sa_column_kwargs={"index": True}
    )

    model_config = ConfigDict(
        extra='forbid',
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, value: datetime, _) -> str:
        if isinstance(value, str):
            value = datetime.fromisoformat(value)
        return value.astimezone(UTC).isoformat() if isinstance(value, datetime) else value