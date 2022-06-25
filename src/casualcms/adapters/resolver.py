from typing import Any

import pkg_resources
from result import Err, Ok, Result


def resolve(value: str) -> Result[Any, str]:
    """return the attr from the syntax: package.module:attr."""
    ep = pkg_resources.EntryPoint.parse(f"x={value}")
    try:
        cls = ep.resolve()
    except ModuleNotFoundError:
        return Err(f"{value} is not a valid.")
    else:
        return Ok(cls)
