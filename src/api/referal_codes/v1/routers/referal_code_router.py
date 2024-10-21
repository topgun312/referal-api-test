from fastapi import APIRouter, status
from fastapi.params import Depends

from src.api.referal_codes.v1.service import ReferalCodeService
from src.api.users.v1.auth.validate import get_current_active_auth_user
from src.schemas.referal_code_schema import (
    CreateReferalCodeRequest,
    ReferalCodeCreateResponse,
    ReferalCodeDB,
    ReferalCodeResponse,
)
from src.schemas.user_schema import UserAuthSchema

router = APIRouter(prefix="/referal_codes", tags=["Referal codes"])


@router.post("/create_referal_code", status_code=status.HTTP_201_CREATED)
async def add_referal_code(
    referal_code_data: CreateReferalCodeRequest,
    service: ReferalCodeService = Depends(ReferalCodeService),
    auth_user: UserAuthSchema = Depends(get_current_active_auth_user),
) -> ReferalCodeCreateResponse:
    """
    Create referal code
    """
    if auth_user:
        code: ReferalCodeDB = await service.create_referal_code_by_referer(
            user_id=auth_user.id, referal_code_data=referal_code_data.model_dump()
        )
        return ReferalCodeCreateResponse(payload=code)


@router.put("/activate_rc", status_code=status.HTTP_200_OK)
async def activate_referal_code(
    referal_code: int,
    service: ReferalCodeService = Depends(ReferalCodeService),
    auth_user: UserAuthSchema = Depends(get_current_active_auth_user),
) -> ReferalCodeResponse:
    """
    Activate referal code
    """
    if auth_user:
        active_code: ReferalCodeDB = await service.activate_referal_code(
            referal_code=referal_code, user_id=auth_user.id
        )
        return ReferalCodeResponse(payload=active_code)


@router.delete("/delete_rc", status_code=status.HTTP_204_NO_CONTENT)
async def delete_referal_code(
    referal_code: int,
    service: ReferalCodeService = Depends(ReferalCodeService),
    auth_user: UserAuthSchema = Depends(get_current_active_auth_user),
) -> None:
    """
    Delete referal code
    """
    if auth_user:
        await service.delete_referal_code(
            referal_code=referal_code, user_id=auth_user.id
        )
