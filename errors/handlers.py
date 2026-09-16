from fastapi import Request
from fastapi.responses import JSONResponse

from psycopg.errors import (
    CheckViolation,
    ForeignKeyViolation,
    NotNullViolation,
    UniqueViolation,
)
from sqlalchemy.exc import IntegrityError, NoResultFound


CHECK_CONSTRAINT_MESSAGES = {
    "chk_training_only_one_main_target":
        "A training cannot have both a certification and a diploma.",
}


async def integrity_error_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:

    if not isinstance(exc, IntegrityError):
        raise exc

    error = exc.orig

    # Foreign key
    if isinstance(error, ForeignKeyViolation):
        return JSONResponse(
            status_code=409,
            content={
                "detail": "Referenced entity does not exist."
            },
        )

    # Unique / duplicate primary or composite key
    if isinstance(error, UniqueViolation):
        return JSONResponse(
            status_code=409,
            content={
                "detail": "Entity already exists."
            },
        )

    # NOT NULL
    if isinstance(error, NotNullViolation):
        return JSONResponse(
            status_code=422,
            content={
                "detail": "Required database field is missing."
            },
        )

    # CHECK
    if isinstance(error, CheckViolation):
        constraint = error.diag.constraint_name

        if constraint is None:
            message = "Database constraint violated."
        else:
            message = CHECK_CONSTRAINT_MESSAGES.get(
                constraint,
                "Database constraint violated.",
            )

        return JSONResponse(
            status_code=422,
            content={
                "detail": message
            },
        )

    # Unknown IntegrityError
    return JSONResponse(
        status_code=409,
        content={
            "detail": "Database integrity constraint violated."
        },
    )


async def no_result_found_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:

    if not isinstance(exc, NoResultFound):
        raise exc

    return JSONResponse(
        status_code=404,
        content={
            "detail": "Entity not found."
        },
    )