# -*- coding: utf-8 -*-
# Date: 28.02.16
from __future__ import absolute_import, unicode_literals


class AbstractBackend(object):
    """
    An abstract backend interface
    """
    def __init__(self, *args, **kwargs):
        raise NotImplemented

    def get(self, key, default=None):
        raise NotImplemented

    def get_many(self, keys, default=None):
        raise NotImplemented

    def set(self, key, value, timeout=None):
        raise NotImplemented

    def delete(self, key):
        raise NotImplemented

    def delete_many(self, keys):
        raise NotImplemented

    def incr(self, key, increment=1):
        raise NotImplemented

    def decr(self, key, decrement=1):
        raise NotImplemented

    def clear(self):
        raise NotImplemented

    flush = clear
