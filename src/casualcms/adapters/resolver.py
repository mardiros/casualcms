from typing import Any

import pkg_resources


def resolve(value: str) -> Any:
    """return the attr from the syntax: package.module:attr."""
    ep = pkg_resources.EntryPoint.parse(f"x={value}")
    cls = ep.resolve()
    return cls
