from typing import Generic, TypeVar

T = TypeVar("T")


class BaseEncoder(Generic[T]):
    def encode(self, value: T) -> T:
        return value
