from fastapi import Body, HTTPException

from .base import router


@router.post("/authntokens")
def authenticate(username: str = Body(...), password: str = Body(...)):
    raise HTTPException(
        status_code=401,
        detail=[{"loc": ["body", "username"], "msg": "Invalid username or password"}],
    )
