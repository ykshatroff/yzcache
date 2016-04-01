# -*- coding: utf-8 -*-
# Date: 28.02.16
from __future__ import absolute_import, unicode_literals
from .abstract import AbstractBackend

__all__ = ('NoopBackend', 'cached_function')


class NoopBackend(AbstractBackend):
    def __init__(self):
        pass

    def get(self, key, default=None):
        return default

    def get_many(self, keys, default=None):
        return {k: default for k in keys}

    def set(self, key, value, timeout=None):
        pass

    def delete(self, key):
        pass

    def delete_many(self, keys):
        pass
