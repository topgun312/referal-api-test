import datetime

from pydantic import BaseModel, Field

from src.schemas.response import BaseCreateResponse, BaseResponse


class ReferalCodeId(BaseModel):
    id: int


class CreateReferalCodeRequest(BaseModel):
    code: int
    days: int
    is_active: bool = Field(default=False)


class UpdateReferalCodeRequest(ReferalCodeId, CreateReferalCodeRequest): ...


class ReferalCodeDB(ReferalCodeId):
    code: int
    is_active: bool
    exp_date: datetime.date


class ReferalCodeResponse(BaseResponse):
    payload: ReferalCodeDB


class ReferalCodeListResponse(BaseResponse):
    payload: list[ReferalCodeDB]


class ReferalCodeCreateResponse(BaseCreateResponse):
    payload: ReferalCodeDB
