import datetime

from pydantic import BaseModel, EmailStr, Field

from src.schemas.referal_code_schema import ReferalCodeDB
from src.schemas.response import BaseCreateResponse, BaseResponse


class UserId(BaseModel):
    id: int


class CreateUserRequest(BaseModel):
    email: EmailStr
    first_name: str = Field(max_length=30)
    last_name: str = Field(max_length=30)
    password: str


class UpdateUserRequest(CreateUserRequest): ...


class UserDB(UserId, CreateUserRequest):
    registered_at: datetime.datetime
    updated_at: datetime.datetime
    referal_codes: list[ReferalCodeDB] = Field(default_factory=list)


class UserAuthSchema(UserId):
    username: EmailStr
    password: bytes
    is_active: bool = True


class Token(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"


class UserResponse(BaseResponse):
    payload: UserDB


class UserListResponse(BaseResponse):
    payload: list[UserDB]


class UserCreateResponse(BaseCreateResponse):
    payload: UserDB
