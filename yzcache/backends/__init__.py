# -*- coding: utf-8 -*-
# Date: 28.02.16
from __future__ import absolute_import, unicode_literals
import importlib


class BackendManager(object):
    DEFAULT_BACKEND = "yzcache.backends.noop.NoopBackend"

    def __init__(self):
        self.backends = {}
        self._default_backend = None
        self._default_backend_name = self.DEFAULT_BACKEND

    def __getitem__(self, item):
        try:
            backend = self.backends[item]
        except KeyError:
            raise ValueError("Not a registered backend %r" % item)
        if isinstance(backend, tuple):
            backend = self.init_backend(*backend)
            self.backends[item] = backend
        return backend

    def add_backend(self, qual_name, backend_name=None, options=None):
        try:
            module_path, class_name = qual_name.rsplit('.', 1)
        except AttributeError:
            raise ValueError("Invalid backend specification")
        if backend_name is None:
            _, backend_name = module_path.rsplit('.', 1)

        self.backends[backend_name] = (module_path, class_name, options)
        return backend_name

    def init_backend(self, module_path, class_name, options):
        backend_module = importlib.import_module(module_path)
        try:
            backend_cls = getattr(backend_module, class_name)
        except AttributeError:
            raise ImportError("Can not import backend '%s.%s'" % (module_path, class_name))

        options = options or {}
        backend = backend_cls(**options)
        return backend

    def get_default_backend(self):
        if self._default_backend is None:
            self._default_backend = self.init_backend(self._default_backend_name)
        return self._default_backend

    def set_default_backend(self, backend, options=None):
        if options is None and isinstance(backend, (list, tuple)):
            try:
                qual_name, backend_name, options = backend
            except ValueError:
                raise ValueError("Invalid backend specification")
        else:
            qual_name = backend
            backend_name = None
        backend_name = self.add_backend(qual_name, backend_name, options)
        self._default_backend_name = backend_name

    default_backend = property(get_default_backend, set_default_backend)


backend_manager = BackendManager()
