class MissingMetaError(Exception):
    def __init__(self, name: str) -> None:
        super().__init__(f"Meta class is missing for block {name}")
