import time
from collections import defaultdict, deque

from ..domain.errors import TooManyAttempts
from ..domain.ports import LoginRateLimiter


class InMemoryLoginRateLimiter(LoginRateLimiter):
    def __init__(self, max_failures: int = 5, window_seconds: int = 300):
        self._max = max_failures
        self._window = window_seconds
        self._failures: dict[str, deque] = defaultdict(deque)

    def _prune(self, key: str) -> deque:
        q = self._failures[key]
        limit = time.time() - self._window
        while q and q[0] < limit:
            q.popleft()
        return q

    def check(self, key: str) -> None:
        if len(self._prune(key)) >= self._max:
            raise TooManyAttempts("Demasiados intentos")

    def register_failure(self, key: str) -> None:
        self._prune(key).append(time.time())

    def reset(self, key: str) -> None:
        self._failures.pop(key, None)
