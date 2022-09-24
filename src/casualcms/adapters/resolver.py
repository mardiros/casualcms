from typing import Any

import pkg_resources
from result import Err, Ok, Result


def resolve(value: str) -> Result[Any, str]:
    """return the attr from the syntax: package.module:attr."""
    ep = pkg_resources.EntryPoint.parse(f"x={value}")
    try:
        cls = ep.resolve()
    except (ImportError, ModuleNotFoundError):
        return Err(f"{value} does not resolve any type.")
    else:
        return Ok(cls)
