import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from dotenv import find_dotenv, load_dotenv
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from loguru import logger
from redis import asyncio as aioredis

from metadata import DESCRIPTION, TAG_METADATA, TITLE, VERSION
from src.api import router
from src.api.referal_codes.v1.routers import rc_router
from src.api.users.v1.routers import auth_router, user_router
from src.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    logger.info("Start redis cache")
    redis = aioredis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
        encoding="utf-8",
        decode_responses=True,
    )
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

    yield
    await redis.close()
    logger.info("Shutdown redis cache")


def create_fastapi_app():
    load_dotenv(find_dotenv(".env"))
    env_name = os.getenv("MODE", "DEV")

    if env_name != "PROD":
        _app = FastAPI(
            default_response_class=ORJSONResponse,
            title=TITLE,
            description=DESCRIPTION,
            version=VERSION,
            openapi_tags=TAG_METADATA,
            lifespan=lifespan,
        )
    else:
        _app = FastAPI(
            default_response_class=ORJSONResponse,
            title=TITLE,
            description=DESCRIPTION,
            version=VERSION,
            openapi_tags=TAG_METADATA,
            lifespan=lifespan,
            docs_url=None,
            redoc_url=None,
        )
    _app.include_router(router=router, prefix="/api")
    _app.include_router(router=user_router, prefix="/api")
    _app.include_router(router=rc_router, prefix="/api")
    _app.include_router(router=auth_router, prefix="/api/auth")

    return _app


app = create_fastapi_app()
