from collections.abc import Sequence

from email_hunter import EmailHunterClient
from fastapi import BackgroundTasks, HTTPException, status
from pydantic import EmailStr

from src.api.referal_codes.v1.referal_utils import validate_referal_code
from src.api.users.v1.auth import utils as auth_utils
from src.config import settings
from src.models import ReferalCodeModel, User
from src.schemas.user_schema import UserDB
from src.utils.service import BaseService
from src.utils.unit_of_work import transaction_mode
from src.workers.email_task import get_referal_code_report

# import clearbit

client = EmailHunterClient(settings.EMAIL_HUNTER_API_KEY)
# clearbit.key = settings.CLEARBIT_API_KEY


class UserService(BaseService):

    @transaction_mode
    async def register_user(self, user_data: dict) -> UserDB:
        user: User | None = await self.uow.user.get_by_query_one_or_none(
            email=user_data["email"]
        )
        self._check_user_already_exists(user=user)
        password = await auth_utils.hash_password(user_data["password"])
        user_data.pop("password")
        new_user: User = await self.uow.user.add_one_and_get_obj(
            password=password, **user_data
        )
        return new_user.to_pydantic_schema()

    @transaction_mode
    async def get_referal_code_by_email(
        self,
        referer_email: EmailStr,
        user_email: EmailStr,
        background_tasks: BackgroundTasks,
    ) -> None:
        referer: User | None = await self.uow.user.get_by_query_one_or_none(
            email=referer_email
        )
        self._check_user_exists(user=referer)
        active_ref_code: ReferalCodeModel | None = (
            await self.uow.referal_code.get_by_query_one_or_none(
                is_active=True, user_id=referer.id
            )
        )
        if active_ref_code:
            get_referal_code_report(
                background_tasks=background_tasks,
                email_to=user_email,
                username=user_email,
                referal_code=active_ref_code.code,
                href="http://127.0.0.1:8000/api/users/end_registration",
                href_name="End registration",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"The user {referer_email} does not have any active referal codes",
            )

    @transaction_mode
    async def end_registration_by_referal_code(
        self, referal_code: int, user_data: dict
    ) -> UserDB:
        validate_rc = validate_referal_code(code=referal_code)
        if validate_rc:
            ref_code: ReferalCodeModel | None = (
                await self.uow.referal_code.get_by_query_one_or_none(code=referal_code)
            )
            self._check_referal_code_exists(code=ref_code)
            user: User | None = await self.uow.user.get_by_query_one_or_none(
                email=user_data["email"]
            )
            self._check_user_already_exists(user=user)
            password = await auth_utils.hash_password(user_data["password"])
            user_data.pop("password")
            new_user: User = await self.uow.user.add_one_and_get_obj(
                password=password, referer_by=ref_code.user_id, **user_data
            )
            return new_user.to_pydantic_schema()

    @transaction_mode
    async def get_user_info(self, email: EmailStr) -> UserDB:
        user: User | None = await self.uow.user.get_by_query_one_or_none(email=email)
        self._check_user_exists(user=user)
        return user.to_pydantic_schema()

    @transaction_mode
    async def get_referals_info(self, referer_id: int) -> Sequence[UserDB]:
        referer: User | None = await self.uow.user.get_by_query_one_or_none(
            id=referer_id
        )
        self._check_user_exists(user=referer)
        referals: Sequence[User] = await self.uow.user.get_all_referals_by_referer(
            referer_id=referer.id
        )
        return [referal.to_pydantic_schema() for referal in referals]

    @transaction_mode
    async def update_user_info(self, email: EmailStr, user_data: dict) -> UserDB:
        user: User | None = await self.uow.user.get_by_query_one_or_none(email=email)
        self._check_user_exists(user=user)
        password = await auth_utils.hash_password(user_data["password"])
        user_data.pop("password")
        update_info_user: User = await self.uow.user.update_one_by_email(
            _email=email, password=password, **user_data
        )
        return update_info_user.to_pydantic_schema()

    @transaction_mode
    async def email_exists_by_emailhunter(self, email: EmailStr):
        user_exists = client.exist(email)
        if user_exists:
            user: User | None = await self.uow.user.get_by_query_one_or_none(
                email=email
            )
            self._check_user_exists(user=user)
            return user.to_pydantic_schema()
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"The user {email} was not found by the emailhunter.co site",
            )

    # @transaction_mode
    # async def user_info_by_email_for_clearbit(self, email: EmailStr):
    #   user_clearbit = clearbit.Enrichment.find(email=email, stream=True)
    #   if user_clearbit:
    #     return user_clearbit
    #   else:
    #     raise HTTPException(
    #       status_code=status.HTTP_404_NOT_FOUND, detail=f"User {email} data is not found on the site clearbit"
    #     )

    @staticmethod
    def _check_user_exists(user: User | None) -> None:
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

    @staticmethod
    def _check_user_already_exists(user: User | None) -> None:
        if user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="User already exists"
            )

    @staticmethod
    def _check_correct_referal_code(code: int | None) -> None:
        if not code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Referal code invalid"
            )

    @staticmethod
    def _check_referal_code_exists(code: ReferalCodeModel | None) -> None:
        if not code:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Referal code not found"
            )
