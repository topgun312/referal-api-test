from sqlalchemy import Result, select, update

from src.models import ReferalCodeModel
from src.utils.repository import SQLAlchemyRepository


class ReferalCodeRepository(SQLAlchemyRepository):

    model = ReferalCodeModel

    async def get_one_active_code(self):
        subq = select(self.model).where(self.model.is_active == True).exists()
        query = select(self.model).where(subq)
        result: Result = await self.session.execute(query)
        return result.scalars().all()

    async def update_one_by_code(
        self, ref_code: int, _user_id: int, **kwargs
    ) -> type(model) | None:
        query = (
            update(self.model)
            .filter(self.model.code == ref_code, self.model.user_id == _user_id)
            .values(**kwargs)
            .returning(self.model)
        )
        result: Result | None = await self.session.execute(query)
        return result.scalar_one_or_none()
