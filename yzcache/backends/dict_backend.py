# -*- coding: utf-8 -*-
# Date: 28.02.16
from __future__ import absolute_import, unicode_literals
import time
from .abstract import AbstractBackend

__all__ = ('DictBackend', )


class DictBackend(AbstractBackend):
    def __init__(self):
        self._cache = {}

    def get(self, key, default=None):
        try:
            val, expires = self._cache[key]
        except KeyError:
            val = default
        else:
            if expires is not None and time.time() > expires:
                val = default
        return val

    def get_many(self, keys, default=None):
        _cache = self._cache
        timestamp = time.time()
        result = {}
        for key in keys:
            try:
                val, expires = _cache[key]
            except KeyError:
                val = default
            else:
                if expires is not None and timestamp > expires:
                    val = default
            result[key] = val
        return result

    def set(self, key, value, timeout=None):
        expires = None if timeout is None else time.time() + timeout
        self._cache[key] = value, expires

    def delete(self, key):
        self._cache.pop(key, None)

    def delete_many(self, keys):
        for key in keys:
            self._cache.pop(key, None)

    def incr(self, key, increment=1):
        pass

    def decr(self, key, decrement=1):
        pass

    def clear(self):
        self._cache.clear()
