import functools
from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from types import TracebackType
from typing import Any

from src.database.db import async_session_maker
from src.repositories import ReferalCodeRepository, UserRepository

AsyncFunc = Callable[..., Awaitable[Any]]


class AbstractUnitOfWork(ABC):
    user: UserRepository
    refelal_code: ReferalCodeRepository

    @abstractmethod
    def __init__(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def __aenter__(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError


class UnitOfWork(AbstractUnitOfWork):

    def __init__(self) -> None:
        self.session_factory = async_session_maker

    async def __aenter__(self) -> None:
        self.session = self.session_factory()
        self.user = UserRepository(self.session)
        self.referal_code = ReferalCodeRepository(self.session)

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if not exc_type:
            await self.commit()
        else:
            await self.rollback()
        await self.session.close()

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()


def transaction_mode(func: AsyncFunc) -> AsyncFunc:
    @functools.wraps(func)
    async def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        async with self.uow:
            return await func(self, *args, **kwargs)

    return wrapper