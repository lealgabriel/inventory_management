from datetime import datetime, timezone
from typing import Any, Generic, List, Optional, Type, TypeVar

from sqlalchemy.orm import joinedload, with_loader_criteria
from sqlmodel import SQLModel, select, and_
from sqlmodel.sql.expression import SelectOfScalar
from sqlmodel.ext.asyncio.session import AsyncSession

from .base_exceptions import NotFoundException


ModelType = TypeVar("ModelType", bound=SQLModel)


class BaseRepository(Generic[ModelType]):
    def __init__(self: 'BaseRepository', model: Type[ModelType]) -> None:
        self.model = model

    def add_eager_join_fields(self, stmt: SelectOfScalar, eager_join_fields: list[str], load_inactive: bool = False) -> SelectOfScalar:
        for field in eager_join_fields:
            relationship_class = self.model.__mapper__.relationships[field].mapper.class_

            conditions = [
                joinedload(getattr(self.model, field)),
                with_loader_criteria(
                    relationship_class, 
                    relationship_class.deleted.is_(False)
                )
            ]

            if not load_inactive and hasattr(relationship_class, "is_active"):
                conditions.append(
                    with_loader_criteria(
                        relationship_class, 
                        relationship_class.is_active.is_(True)
                    )
                )

            stmt = stmt.options(*conditions)

        return stmt

    async def add(self: 'BaseRepository', item: ModelType, db: AsyncSession) -> ModelType:
        db.add(item)
        await db.flush()
        await db.refresh(item)
        return item

    async def get(
        self: 'BaseRepository', 
        id: int, 
        db: AsyncSession, 
        eager_join_fields: Optional[list[str]] = None, 
        load_inactive_relationship: bool = False
    ) -> ModelType:
        stmt = select(self.model).where(
            and_(
                self.model.id == id,
                self.model.deleted.is_(False)
            )
        )

        if eager_join_fields:
            stmt = self.add_eager_join_fields(stmt, eager_join_fields, load_inactive_relationship)

        result = await db.scalars(stmt)

        record = result.unique().first()

        if not record:
            raise NotFoundException(f'Item not found with id: {id}')

        return record

    async def list(
        self: 'BaseRepository',
        db: AsyncSession,
        skip: int = 0,
        limit: int = 50,
        filters: dict[str, Any] | None = None,
        eager_join_fields: Optional[list[str]] = None,
        load_inactive_relationship: bool = False
    ) -> List[ModelType]:
        stmt = select(self.model).where(self.model.deleted.is_(False)).order_by(self.model.id).offset(skip).limit(limit)

        if eager_join_fields:
            stmt = self.add_eager_join_fields(stmt, eager_join_fields, load_inactive_relationship)

        if filters:
            model_filters = {attr: value for attr, value in filters.items() if attr not in ['skip', 'limit']}

            for attr, value in model_filters.items():
                stmt = stmt.where(getattr(self.model, attr) == value)

        results = await db.scalars(stmt)

        records = results.unique().all()

        return records

    async def update(
        self: 'BaseRepository',
        model: ModelType,
        item: Type[ModelType],
        db: AsyncSession,
    ) -> ModelType:
        obj_data = model.model_dump()
        update_data = item.model_dump(exclude_unset=True, exclude={"updated_at", "created_at"})

        for field in obj_data:
            if field in update_data:
                setattr(model, field, update_data[field])

        model = await db.merge(model)
        await db.flush()
        await db.refresh(model)
        return model

    async def delete(self: 'BaseRepository', id: int, db: AsyncSession) -> None:
        record = await self.get(id, db)

        record.deleted = True

        await db.flush()
        await db.refresh(record)