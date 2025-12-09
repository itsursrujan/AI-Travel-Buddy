# backend/services/cache_service.py
import time
import threading
from typing import Optional, Tuple

class CacheService:
    """Simple thread-safe in-memory TTL cache for small binary objects.

    Note: Suitable for development. For production use Redis or similar.
    """
    def __init__(self, default_ttl: int = 24 * 3600):
        self._store = {}  # key -> (expires_at, content_type, bytes)
        self._lock = threading.Lock()
        self._ttl = default_ttl

    def get(self, key: str) -> Optional[Tuple[str, bytes]]:
        now = time.time()
        with self._lock:
            val = self._store.get(key)
            if not val:
                return None
            expires_at, content_type, data = val
            if expires_at < now:
                # expired
                del self._store[key]
                return None
            return (content_type, data)

    def set(self, key: str, content_type: str, data: bytes, ttl: Optional[int] = None):
        expires = time.time() + (ttl if ttl is not None else self._ttl)
        with self._lock:
            self._store[key] = (expires, content_type, data)

    def clear(self):
        with self._lock:
            self._store.clear()

# Provide a module-level default cache instance for convenience
default_cache = CacheService()
