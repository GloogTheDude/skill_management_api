import os
from contextlib import asynccontextmanager

from sqlalchemy.exc import IntegrityError, NoResultFound
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from sqlalchemy.orm import Session
from core.cache import custom_key_builder

from controllers import (
    certification_controller,
    certification_skill_controller,
    skill_controller,
    domaine_controller,
    training_source_controller,
    diploma_controller,
    training_controller,
    training_skill_controller,
    diploma_skill_controller,
    validation_type_controller,
    employee_controller,
    role_controller,
    access_level_controller,
    skill_validation_controller,
    employee_diploma_controller,
    employee_certification_controller,
    employee_declared_skill_controller,
    employee_certification_expiration_controller,
    available_training_controller,
    participation_controller,
    training_request_controller,
    employee_skill_profile_controller,
    employee_skill_search_controller,
    auth_controller,
    dashboard_controller,
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        ).split(",")
        if origin.strip()
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(
    IntegrityError,
    integrity_error_handler,
)

app.add_exception_handler(
    NoResultFound,
    no_result_found_handler,
)

app.include_router(skill_controller.router)
app.include_router(domaine_controller.router)
app.include_router(training_source_controller.router)
app.include_router(certification_controller.router)
app.include_router(diploma_controller.router)
app.include_router(training_controller.router)
app.include_router(training_skill_controller.router)
app.include_router(certification_skill_controller.router)
app.include_router(diploma_skill_controller.router)
app.include_router(validation_type_controller.router)
app.include_router(employee_controller.router)
app.include_router(role_controller.router)
app.include_router(access_level_controller.router)
app.include_router(skill_validation_controller.router)
app.include_router(employee_diploma_controller.router)
app.include_router(employee_certification_controller.router)
app.include_router(employee_declared_skill_controller.router)
app.include_router(employee_certification_expiration_controller.router)
app.include_router(available_training_controller.router)
app.include_router(participation_controller.router)
app.include_router(training_request_controller.router)
app.include_router(employee_skill_profile_controller.router)
app.include_router(employee_skill_search_controller.router)
app.include_router(auth_controller.router)
app.include_router(dashboard_controller.router)



if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8001,
        reload=True,
    )
