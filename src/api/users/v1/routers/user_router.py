from collections.abc import Sequence

from fastapi import APIRouter, BackgroundTasks, Depends, status
from fastapi_cache.decorator import cache
from pydantic import EmailStr

from src.api.users.v1.auth.validate import get_current_active_auth_user
from src.api.users.v1.service.user_service import UserService
from src.schemas.user_schema import (
    CreateUserRequest,
    UpdateUserRequest,
    UserAuthSchema,
    UserCreateResponse,
    UserDB,
    UserListResponse,
    UserResponse,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: CreateUserRequest, service: UserService = Depends(UserService)
) -> UserCreateResponse:
    """
    Register new user
    """
    user: UserDB = await service.register_user(user_data=user_data.model_dump())
    return UserCreateResponse(payload=user)


@router.get("/get_rc_by_email", status_code=status.HTTP_200_OK)
async def get_referal_code_by_email(
    referer_email: EmailStr,
    user_email: EmailStr,
    background_tasks: BackgroundTasks,
    service: UserService = Depends(UserService),
) -> dict[str, int | str]:
    """
    Receiving referal code by email
    """
    await service.get_referal_code_by_email(
        referer_email=referer_email,
        user_email=user_email,
        background_tasks=background_tasks,
    )
    return {
        "status_code": status.HTTP_200_OK,
        "detail": f"A message with an referal_code has been sent to email {user_email}",
    }


@router.post("/end_registration", status_code=status.HTTP_201_CREATED)
async def end_registration_by_referal_code(
    referal_code: int,
    user_data: CreateUserRequest,
    service: UserService = Depends(UserService),
) -> UserCreateResponse:
    """
    End registration after receiving the referal code
    """
    user: UserDB = await service.end_registration_by_referal_code(
        referal_code=referal_code, user_data=user_data.model_dump()
    )
    return UserCreateResponse(payload=user)


@router.get("/user_info", status_code=status.HTTP_200_OK)
@cache(expire=3600)
async def get_user_info_by_email(
    email: EmailStr,
    service: UserService = Depends(UserService),
    auth_user: UserAuthSchema = Depends(get_current_active_auth_user),
) -> UserResponse:
    """
    Getting user information by email
    """
    if auth_user:
        user: UserDB = await service.get_user_info(email=email)
        return UserResponse(payload=user)


@router.get("/referals_info", status_code=status.HTTP_200_OK)
@cache(expire=3600)
async def get_referals_info_by_referer_id(
    referer_id: int,
    service: UserService = Depends(UserService),
    auth_user: UserAuthSchema = Depends(get_current_active_auth_user),
) -> UserListResponse:
    """
    Getting information about referals by referrer id
    """
    if auth_user:
        users: Sequence[UserDB] = await service.get_referals_info(referer_id=referer_id)
        return UserListResponse(payload=users)


@router.put("/update_user_info", status_code=status.HTTP_200_OK)
async def update_user_info(
    email: EmailStr,
    user_data: UpdateUserRequest,
    service: UserService = Depends(UserService),
    auth_user: UserAuthSchema = Depends(get_current_active_auth_user),
) -> UserResponse:
    """
    Editing user information
    """
    if auth_user:
        user: UserDB = await service.update_user_info(
            email=email, user_data=user_data.model_dump()
        )
        return UserResponse(payload=user)


@router.get("/email_exists", status_code=status.HTTP_200_OK)
@cache(expire=3600)
async def get_email_exists_by_emailhunter(
    email: EmailStr,
    service: UserService = Depends(UserService),
    auth_user: UserAuthSchema = Depends(get_current_active_auth_user),
) -> UserResponse:
    """
    Checking for the existence of an email using the site emailhunter.co
    """
    if auth_user:
        user: UserDB = await service.email_exists_by_emailhunter(email=email)
        return UserResponse(payload=user)
    # Error : Unfortunately, it isn't possible to sign up using a webmail address. Please use a professional email address instead (for example youraddress@yourcompany.com).


# @router.get("/user_info_for_clearbit", status_code=status.HTTP_200_OK)
# async def get_user_info_by_email_for_clearbit(email: EmailStr,
#                                               service: UserService = Depends(UserService),
#                                               auth_user: UserAuthSchema = Depends(get_current_active_auth_user)) -> dict:
#   """
#   Getting additional information about the user from the clearbit.com website
#   """
#   if auth_user:
#     user: dict = await service.user_info_by_email_for_clearbit(email=email)
#     return user

# Error : Note: This error originates from the build backend, and is likely not a problem with poetry but with clearbit (0.1.7) not supporting PEP 517 builds. You can verify this by running 'pip wheel --no-cache-dir --use-pep517 "clearbit (==0.1.7)"'.
