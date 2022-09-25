import secrets
import uuid


def generate_id() -> str:
    return str(uuid.uuid1())


def generate_secret() -> str:
    return secrets.token_urlsafe(64)
