import os
from contextlib import asynccontextmanager

from sqlalchemy.exc import IntegrityError, NoResultFound
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from sqlalchemy.orm import Session
from core.cache import custom_key_builder

from controlers import (
    certification_controler,
    skill_controler,
    domaine_controler,
    training_source_controler,
    diploma_controler,
    training_controller
)

from errors.handlers import (
    integrity_error_handler,
    no_result_found_handler,
)
load_dotenv()



@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = aioredis.from_url(
        os.getenv("LOCAL_REDIS_URL", "redis://127.0.0.1:6379/0")
    )

    FastAPICache.init(
        RedisBackend(redis),
        prefix="api2-cache",
        key_builder=custom_key_builder,
    )
    
    app.state.redis = redis

    print("Redis cache initialized")

    yield

    await redis.close()
    print("FastAPI shutting down")


app = FastAPI(lifespan=lifespan)

app.add_exception_handler(
    IntegrityError,
    integrity_error_handler,
)

app.add_exception_handler(
    NoResultFound,
    no_result_found_handler,
)

app.include_router(skill_controler.router)
app.include_router(domaine_controler.router)
app.include_router(training_source_controler.router)
app.include_router(certification_controler.router)
app.include_router(diploma_controler.router)
app.include_router(training_controller.router)



if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8001,
        reload=True,
    )