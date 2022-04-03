from typing import Any

from fastapi import Body, HTTPException


def authenticate(username: str = Body(...), password: str = Body(...)) -> Any:
    raise HTTPException(
        status_code=401,
        detail=[{"loc": ["body", "username"], "msg": "Invalid username or password"}],
    )
