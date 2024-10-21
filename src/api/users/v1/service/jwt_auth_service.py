from fastapi import HTTPException, status
from pydantic import EmailStr

from src.schemas.user_schema import UserAuthSchema
from src.utils.service import BaseService
from src.utils.unit_of_work import transaction_mode


class JWTAuthService(BaseService):
    @transaction_mode
    async def get_user(
        self,
        username: EmailStr,
    ) -> UserAuthSchema:
        """Get user by email"""
        user = await self.uow.user.get_by_query_one_or_none(email=username)
        if user:
            return UserAuthSchema(
                id=user.id,
                username=user.email,
                password=user.password,
                is_active=user.is_active,
            )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="user unactive"
        )
