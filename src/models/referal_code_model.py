from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base_model import BaseModel
from src.models.mixins.custom_types import integer_pk
from src.schemas.referal_code_schema import ReferalCodeDB

if TYPE_CHECKING:
    from src.models import User


class ReferalCodeModel(BaseModel):
    __tablename__ = "referal_code_table"

    id: Mapped[integer_pk]
    code: Mapped[int] = mapped_column(nullable=False)
    exp_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user_table.id", ondelete="CASCADE")
    )
    user: Mapped["User"] = relationship(back_populates="referal_codes")

    def to_pydantic_schema(self) -> ReferalCodeDB:
        return ReferalCodeDB(**self.__dict__)
