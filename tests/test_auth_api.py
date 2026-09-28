import asyncio
from types import SimpleNamespace

import pytest
from fastapi import HTTPException, Response
from starlette.requests import Request

from controllers.auth_controller import get_current_employee, login, logout
from core.auth import SESSION_KEY_PREFIX, SESSION_TTL_SECONDS, RedisSessionStore
from core.security import hash_password
from dto.auth_dto import LoginDTO
from services.auth_service import AuthService


class FakeRedis:
    def __init__(self):
        self.values = {}
        self.set_calls = []
        self.deleted_keys = []

    async def set(self, key, value, ex=None):
        self.values[key] = str(value)
        self.set_calls.append((key, str(value), ex))

    async def get(self, key):
        return self.values.get(key)

    async def delete(self, key):
        self.deleted_keys.append(key)
        self.values.pop(key, None)


class FakeEmployeeRepository:
    def __init__(self, employees):
        self.employees = {employee.id_employee: employee for employee in employees}

    def get_active_by_mail(self, mail):
        return next(
            (
                employee
                for employee in self.employees.values()
                if employee.mail == mail and not employee.is_deleted
            ),
            None,
        )

    def get_active_by_id(self, id_employee):
        employee = self.employees.get(id_employee)
        if employee is None or employee.is_deleted:
            return None
        return employee


def make_employee(*, deleted=False):
    access_level = SimpleNamespace(label="Manager", level=2)
    role = SimpleNamespace(denomination_role="Manager IT", access_level=access_level)
    return SimpleNamespace(
        id_employee=1,
        first_name="Test",
        last_name="Employee",
        mail="test@example.com",
        hash_password=hash_password("secret"),
        id_role=2,
        is_deleted=deleted,
        role=role,
    )


def run(coroutine):
    return asyncio.run(coroutine)


def request_with_cookie(session_id: str | None = None) -> Request:
    headers = []
    if session_id is not None:
        headers.append((b"cookie", f"session_id={session_id}".encode()))
    return Request({"type": "http", "headers": headers})


@pytest.fixture
def auth_context():
    redis = FakeRedis()
    employee = make_employee()
    service = AuthService(
        FakeEmployeeRepository([employee]),
        RedisSessionStore(redis),
    )
    return service, redis, employee


def test_login_sets_opaque_http_only_cookie_and_stores_ttl(auth_context):
    service, redis, _ = auth_context
    response = Response()

    body = run(
        login(
            LoginDTO(mail="test@example.com", password="secret"),
            response,
            service,
        )
    ).model_dump()

    assert body["id_employee"] == 1
    assert "password" not in body
    assert "hash_password" not in body
    set_cookie = response.headers["set-cookie"]
    assert "session_id=" in set_cookie
    assert "HttpOnly" in set_cookie
    assert "SameSite=lax" in set_cookie
    assert "Path=/" in set_cookie
    assert "Secure" not in set_cookie
    assert len(redis.set_calls) == 1
    key, employee_id, ttl = redis.set_calls[0]
    assert key.startswith(SESSION_KEY_PREFIX)
    assert employee_id == "1"
    assert ttl == SESSION_TTL_SECONDS
    assert "secret" not in redis.values[key]


def test_invalid_credentials_are_indistinguishable(auth_context):
    service, redis, _ = auth_context

    with pytest.raises(HTTPException) as wrong_password:
        run(login(LoginDTO(mail="test@example.com", password="wrong"), Response(), service))
    with pytest.raises(HTTPException) as unknown_mail:
        run(login(LoginDTO(mail="unknown@example.com", password="secret"), Response(), service))

    assert wrong_password.value.status_code == 401
    assert unknown_mail.value.status_code == 401
    assert wrong_password.value.detail == unknown_mail.value.detail
    assert redis.set_calls == []


def test_deleted_employee_cannot_login(auth_context):
    service, _, employee = auth_context
    employee.is_deleted = True

    with pytest.raises(HTTPException) as result:
        run(login(LoginDTO(mail="test@example.com", password="secret"), Response(), service))

    assert result.value.status_code == 401


def test_two_logins_create_different_sessions(auth_context):
    service, redis, _ = auth_context
    first_response = Response()
    second_response = Response()

    run(login(LoginDTO(mail="test@example.com", password="secret"), first_response, service))
    run(login(LoginDTO(mail="test@example.com", password="secret"), second_response, service))

    assert len(redis.set_calls) == 2
    assert redis.set_calls[0][0] != redis.set_calls[1][0]
    assert redis.set_calls[0][0] != f"{SESSION_KEY_PREFIX}1"
    assert len(redis.set_calls[0][0].removeprefix(SESSION_KEY_PREFIX)) > 20
    assert first_response.headers["set-cookie"] != second_response.headers["set-cookie"]


def test_me_resolves_session_and_public_employee_data(auth_context):
    service, redis, employee = auth_context
    session_id = run(RedisSessionStore(redis).create(employee.id_employee))

    body = run(get_current_employee(request_with_cookie(session_id), service)).model_dump()

    assert body["id_employee"] == 1
    assert body["role_name"] == "Manager IT"
    assert body["access_level_label"] == "Manager"
    assert body["access_level"] == 2
    assert "password" not in body
    assert "hash_password" not in body


@pytest.mark.parametrize("session_id", [None, "unknown"])
def test_me_rejects_missing_or_unknown_session(auth_context, session_id):
    service, _, _ = auth_context

    with pytest.raises(HTTPException) as result:
        run(get_current_employee(request_with_cookie(session_id), service))

    assert result.value.status_code == 401


def test_me_rejects_employee_deleted_after_login(auth_context):
    service, redis, employee = auth_context
    session_id = run(RedisSessionStore(redis).create(employee.id_employee))
    employee.is_deleted = True

    with pytest.raises(HTTPException) as result:
        run(get_current_employee(request_with_cookie(session_id), service))

    assert result.value.status_code == 401


def test_logout_deletes_session_and_cookie(auth_context):
    service, redis, employee = auth_context
    session_id = run(RedisSessionStore(redis).create(employee.id_employee))
    response = Response(status_code=204)

    run(logout(request_with_cookie(session_id), response, service))

    assert f"{SESSION_KEY_PREFIX}{session_id}" in redis.deleted_keys
    assert 'session_id="";' in response.headers["set-cookie"]
    assert "Max-Age=0" in response.headers["set-cookie"]


def test_logout_without_session_is_idempotent(auth_context):
    service, redis, _ = auth_context
    response = Response(status_code=204)

    run(logout(request_with_cookie(), response, service))

    assert redis.deleted_keys == []
