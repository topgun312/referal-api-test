from collections.abc import Sequence
from typing import Any

from pydantic import EmailStr
from sqlalchemy import Result, select, update

from src.models import User
from src.utils.repository import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository):
    model = User

    async def get_all_referals_by_referer(
        self, referer_id: int
    ) -> Sequence[type(model)]:
        query = select(self.model).filter(self.model.referer_by == referer_id)
        result: Result = await self.session.execute(query)
        return result.scalars().all()

    async def update_one_by_email(
        self, _email: EmailStr, **kwargs: Any
    ) -> type(model) | None:
        query = (
            update(self.model)
            .filter(self.model.email == _email)
            .values(**kwargs)
            .returning(self.model)
        )
        obj: Result | None = await self.session.execute(query)
        return obj.scalar_one_or_none()
