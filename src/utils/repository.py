from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any

from sqlalchemy import delete, insert, select, update
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession


class AbstractRepository(ABC):
    @abstractmethod
    async def add_one(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def add_one_and_get_id(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def add_one_and_get_obj(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def get_by_query_one_or_none(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def get_by_query_all(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def update_one_by_id(self, *args: Any, **kwargs: Any):
        raise NotImplementedError

    @abstractmethod
    async def delete_by_query(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def delete_all(self, *args, **kwargs):
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository):
    model = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_one(self, **kwargs) -> None:
        query = insert(self.model).values(**kwargs)
        await self.session.execute(query)

    async def add_one_and_get_id(self, **kwargs) -> int:
        query = insert(self.model).values(**kwargs).returning(self.id)
        _id: Result = await self.session.execute(query)
        return _id.scalar_one()

    async def add_one_and_get_obj(self, **kwargs) -> type(model):
        query = insert(self.model).values(**kwargs).returning(self.model)
        _object: Result = await self.session.execute(query)
        return _object.scalar_one()

    async def get_by_query_one_or_none(self, **kwargs) -> type(model) | None:
        query = select(self.model).filter_by(**kwargs)
        result: Result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()

    async def get_by_query_all(self, **kwargs) -> Sequence[type(model)]:
        query = select(self.model).filter_by(**kwargs)
        result: Result = await self.session.execute(query)
        return result.scalars().all()

    async def update_one_by_id(self, obj_id: int, **kwargs: Any) -> type(model) | None:
        query = (
            update(self.model)
            .filter(self.model.id == obj_id)
            .values(**kwargs)
            .returning(self.model)
        )
        obj: Result | None = await self.session.execute(query)
        return obj.scalar_one_or_none()

    async def delete_by_query(self, **kwargs) -> None:
        query = delete(self.model).filter_by(**kwargs)
        await self.session.execute(query)

    async def delete_all(self) -> None:
        query = delete(self.model)
        await self.session.execute(query)
