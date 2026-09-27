from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from core.auth import (
    AUTH_COOKIE_SAMESITE,
    AUTH_COOKIE_SECURE,
    SESSION_COOKIE_NAME,
    SESSION_TTL_SECONDS,
    RedisSessionStore,
)
from core.database import get_session
from db.repositories.employee_repository import EmployeeRepository
from dto.auth_dto import AuthEmployeeDTO, LoginDTO
from services.auth_service import AuthService


router = APIRouter(prefix="/auth", tags=["auth"])


def get_auth_service(
    request: Request,
    session: Session = Depends(get_session),
) -> AuthService:
    return AuthService(
        EmployeeRepository(session),
        RedisSessionStore(request.app.state.redis),
    )


def _authentication_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials.",
        headers={"WWW-Authenticate": "Session"},
    )


@router.post("/login", response_model=AuthEmployeeDTO)
async def login(
    dto: LoginDTO,
    response: Response,
    service: AuthService = Depends(get_auth_service),
) -> AuthEmployeeDTO:
    result = await service.login(dto.mail, dto.password)
    if result is None:
        raise _authentication_error()

    session_id, employee = result
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=session_id,
        httponly=True,
        secure=AUTH_COOKIE_SECURE,
        samesite=AUTH_COOKIE_SAMESITE,
        path="/",
        max_age=SESSION_TTL_SECONDS,
    )
    return employee


async def get_current_employee(
    request: Request,
    service: AuthService = Depends(get_auth_service),
) -> AuthEmployeeDTO:
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={"WWW-Authenticate": "Session"},
        )

    employee = await service.get_current_employee(session_id)
    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={"WWW-Authenticate": "Session"},
        )
    return employee


@router.get("/me", response_model=AuthEmployeeDTO)
async def get_me(
    employee: AuthEmployeeDTO = Depends(get_current_employee),
) -> AuthEmployeeDTO:
    return employee


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request,
    response: Response,
    service: AuthService = Depends(get_auth_service),
) -> Response:
    await service.logout(request.cookies.get(SESSION_COOKIE_NAME))
    response.delete_cookie(
        key=SESSION_COOKIE_NAME,
        path="/",
    )
    return response
