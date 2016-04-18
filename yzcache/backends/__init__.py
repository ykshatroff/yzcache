# -*- coding: utf-8 -*-
# Date: 28.02.16
from __future__ import absolute_import, unicode_literals
import importlib


class WrongBackendError(KeyError):
    """Raised if no backend found"""


class BackendManager(object):
    DEFAULT_BACKEND = "yzcache.backends.noop.NoopBackend"

    WrongBackendError = WrongBackendError

    def __init__(self):
        self.backends = {}

        self._default_backend = None

        self._default_backend_name = self.DEFAULT_BACKEND

    def __getitem__(self, item):
        if item is None:
            item = self._default_backend_name
        try:
            backend = self.backends[item]
        except KeyError:
            raise WrongBackendError("Not a registered backend %r" % item)
        if isinstance(backend, tuple):
            backend = self.init_backend(*backend)
            self.backends[item] = backend
        return backend

    def add_backend(self, qual_name, backend_name=None, options=None):
        """Lazily add a backend

        :param qual_name: python module path
        :param backend_name: optional name for the backend, default: the backend's leaf module name
        :param options: a dict of kwargs to the backend's ``__init__``
        :return: str
        """
        try:
            module_path, class_name = qual_name.rsplit('.', 1)
        except AttributeError:
            raise WrongBackendError("Invalid backend specification")
        except ValueError:
            module_path, class_name = 'yzcache.backends.%s' % qual_name, None
        if backend_name is None:
            _, backend_name = module_path.rsplit('.', 1)

        self.backends[backend_name] = (module_path, class_name, options)
        return backend_name

    def init_backend(self, module_path, class_name, options):
        """Really initialize the backend

        :param module_path:
        :param class_name:
        :param options:
        :return: backend object
        :raise: ImportError
        """
        backend_module = importlib.import_module(module_path)
        try:
            if class_name:
                backend_cls = getattr(backend_module, class_name)
            else:
                backend_cls = getattr(backend_module, backend_module.__all__[0])
        except AttributeError:
            raise ImportError("Can not import backend '%s.%s'" % (module_path, class_name))

        options = options or {}
        backend = backend_cls(**options)
        return backend

    def get_default_backend(self):
        if self._default_backend is None:
            self._default_backend = self.add_backend(self._default_backend_name)
        return self[self._default_backend]

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
