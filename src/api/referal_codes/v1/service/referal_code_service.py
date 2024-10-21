from datetime import datetime, timedelta

from fastapi import HTTPException, status

from src.models import ReferalCodeModel
from src.schemas.referal_code_schema import ReferalCodeDB
from src.utils.service import BaseService
from src.utils.unit_of_work import transaction_mode


class ReferalCodeService(BaseService):

    @transaction_mode
    async def create_referal_code_by_referer(
        self, user_id: int, referal_code_data: dict
    ) -> ReferalCodeDB:
        code = referal_code_data["code"]
        ref_code: ReferalCodeModel | None = (
            await self.uow.referal_code.get_by_query_one_or_none(code=code)
        )
        self._check_referal_code_already_exists(code=ref_code)
        exp_date = datetime.now().date() + timedelta(days=referal_code_data["days"])
        if referal_code_data["is_active"] == True:
            active_ref_code = await self.uow.referal_code.get_one_active_code()
            if not active_ref_code:
                new_ref_code: ReferalCodeModel = (
                    await self.uow.referal_code.add_one_and_get_obj(
                        code=code, exp_date=exp_date, is_active=True, user_id=user_id
                    )
                )
                return new_ref_code.to_pydantic_schema()
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Active referal code already exists",
                )
        else:
            new_ref_code: ReferalCodeModel = (
                await self.uow.referal_code.add_one_and_get_obj(
                    code=code, exp_date=exp_date, is_active=False, user_id=user_id
                )
            )
            return new_ref_code.to_pydantic_schema()

    @transaction_mode
    async def activate_referal_code(
        self, referal_code: int, user_id: int
    ) -> ReferalCodeDB:
        ref_code: ReferalCodeModel | None = (
            await self.uow.referal_code.get_by_query_one_or_none(code=referal_code)
        )
        self._check_referal_code_exists(code=ref_code)
        active_ref_code = await self.uow.referal_code.get_one_active_code()
        if len(active_ref_code) == 0:
            if ref_code.exp_date >= datetime.now().date():
                if ref_code.user_id == user_id:
                    update_ref_code: ReferalCodeModel = (
                        await self.uow.referal_code.update_one_by_code(
                            ref_code=referal_code, _user_id=user_id, is_active=True
                        )
                    )
                    return update_ref_code.to_pydantic_schema()
                else:
                    self._checking_the_codes_ownership()
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="The referal code has expired. Please create a new referal code",
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Active referal code already exists",
            )

    @transaction_mode
    async def delete_referal_code(self, referal_code: int, user_id: int) -> None:
        ref_code: ReferalCodeModel | None = (
            await self.uow.referal_code.get_by_query_one_or_none(code=referal_code)
        )
        self._check_referal_code_exists(code=ref_code)
        if ref_code.user_id == user_id:
            await self.uow.referal_code.delete_by_query(
                code=referal_code, user_id=user_id
            )
        else:
            self._checking_the_codes_ownership()

    @staticmethod
    def _check_referal_code_already_exists(code: ReferalCodeModel | None) -> None:
        if code:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Referal code already exists",
            )

    @staticmethod
    def _check_referal_code_exists(code: ReferalCodeModel | None) -> None:
        if not code:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Referal code not found"
            )

    @staticmethod
    def _checking_the_codes_ownership() -> None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can activate or delete only the referal code created by you",
        )
