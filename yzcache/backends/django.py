# -*- coding: utf-8 -*-
# Date: 20.04.16
from __future__ import absolute_import, unicode_literals


from .abstract import AbstractBackend

__all__ = ('DjangoBackend', )


class DjangoBackend(AbstractBackend):
    def __init__(self, name=None, **options):
        # import after django's settings were initialized
        from django.core.cache import caches
        self._cache = caches[name]

    def __getattr__(self, item):
        return getattr(self._cache, item)
