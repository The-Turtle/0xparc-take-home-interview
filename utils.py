from __future__ import annotations

from functools import wraps
from types import TracebackType
from typing import Callable, ClassVar, TypeVar
from typing import ParamSpec

P = ParamSpec("P")  # P captures the parameters (arguments) of the function
R = TypeVar("R")  # R captures the return type of the function

class CallCounter:
    current_context: ClassVar[CallCounter | None] = None
    counts: dict[str, int]  # Store counts as a dictionary: {"MethodName": count}

    def __init__(self) -> None:
        self.counts = {}

    def __enter__(self) -> CallCounter:
        CallCounter.current_context = self
        return self

    def __exit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None) -> None:
        CallCounter.current_context = None


def count_calls(func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        ctx = CallCounter.current_context
        if ctx is not None:
            name = func.__qualname__
            ctx.counts[name] = ctx.counts.get(name, 0) + 1
        return func(*args, **kwargs)

    return wrapper
