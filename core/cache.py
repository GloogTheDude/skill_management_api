import hashlib

from sqlalchemy.orm import Session


def custom_key_builder(
    func,
    namespace="",
    *,
    request=None,
    response=None,
    args,
    kwargs,
):
    filtered_kwargs = {
        key: value
        for key, value in kwargs.items()
        if not isinstance(value, Session)
    }

    raw_key = (
        f"{func.__module__}:"
        f"{func.__name__}:"
        f"{args}:"
        f"{filtered_kwargs}"
    )

    hashed_key = hashlib.md5(
        raw_key.encode()
    ).hexdigest()

    return f"{namespace}:{hashed_key}"