from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils import EmailType

from src.models.base_model import BaseModel
from src.models.mixins.custom_types import created_at_ct, integer_pk, updated_at_ct
from src.schemas.user_schema import UserDB

if TYPE_CHECKING:
    from src.models import ReferalCodeModel


class User(BaseModel):
    __tablename__ = "user_table"

    id: Mapped[integer_pk]
    first_name: Mapped[str] = mapped_column(String(30))
    last_name: Mapped[str] = mapped_column(String(30))
    email: Mapped[str] = mapped_column(EmailType, nullable=False, unique=True)
    registered_at: Mapped[created_at_ct]
    updated_at: Mapped[updated_at_ct]
    password: Mapped[bytes] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    referer_by: Mapped[int] = mapped_column(nullable=False, default=0)
    referal_codes: Mapped[list["ReferalCodeModel"]] = relationship(
        back_populates="user"
    )

    def to_pydantic_schema(self) -> UserDB:
        return UserDB(**self.__dict__)
