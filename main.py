import os
from contextlib import asynccontextmanager

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from sqlalchemy.orm import Session
from core.cache import custom_key_builder

from controlers import (
    skill_controler,
    domaine_controler,
    training_source_controler
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

app.include_router(skill_controler.router)
app.include_router(domaine_controler.router)
app.include_router(training_source_controler.router)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )