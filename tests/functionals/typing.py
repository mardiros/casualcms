from typing import Protocol

from .fixtures import Browser


class Context(Protocol):
    browser: Browser
