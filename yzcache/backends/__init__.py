# -*- coding: utf-8 -*-
# Date: 28.02.16
from __future__ import absolute_import, unicode_literals
import importlib
import os
import six
from .abstract import AbstractBackend as Backend

DEFAULTS = {
    'default': {
        'class': 'yzcache.backends.noop.NoopBackend',
        'options': None,
    }
}


class WrongBackendError(KeyError):
    """Raised if no backend found"""


class BackendManager(object):
    DEFAULT_BACKEND = "default"

    WrongBackendError = WrongBackendError

    def __init__(self):
        try:
            settings = os.environ['YZCACHE_SETTINGS']
        except KeyError:
            try:
                from django.conf import settings as django_settings
                settings = django_settings.YZCACHE_SETTINGS
            except ImportError:
                settings = DEFAULTS
        else:
            try:
                module_path, attr = settings.rsplit('.', 1)
            except (AttributeError, ValueError):
                raise WrongBackendError("Invalid settings object specification: "
                                        "must be a dotted object name, got %r" % settings)
            try:
                mod = importlib.import_module(module_path)
                settings = getattr(mod, attr)
            except (ImportError, AttributeError):
                raise WrongBackendError("Failed to import settings object %r" % settings)

        try:
            for name, config in settings.items():
                if isinstance(config, six.string_types):
                    settings[name] = {'class': config}
                elif not isinstance(config, dict):
                    raise WrongBackendError("Invalid config for backend %r: "
                                            "must be a dict, got %s" % (name, type(config)))
                elif not isinstance(config.get('class', ""), six.string_types):
                    raise WrongBackendError("Invalid config for backend %r: "
                                            "'class' must be a string, got %s" % (name, type(config['class'])))

        except (TypeError, AttributeError):
            raise WrongBackendError("Invalid settings object %r: "
                                    "must be a dict, got %s" % (settings, type(settings)))

        default_backend = self.DEFAULT_BACKEND
        if default_backend not in settings and len(settings) == 1:
            default_backend = settings.keys()[0]

        self.config = settings
        self.backends = {}  # type: dict[str, Backend]
        self._default_backend = default_backend

    def __getitem__(self, item):
        if item is None:
            item = self._default_backend
        try:
            backend = self.backends[item]
        except KeyError:
            # Lazy initialization
            try:
                backend_config = self.config[item]
            except KeyError:
                raise WrongBackendError("Not a registered backend %r" % item)

            backend = self.init_backend(backend_config.get('class', item),
                                        options=backend_config.get('options'))
            self.backends[item] = backend
        return backend

    def add_backend(self, qual_name, backend_name=None, options=None):
        """Add a backend config

        :param qual_name: python module path
        :param backend_name: optional name for the backend, default: the backend's leaf module name
        :param options: a dict of kwargs to the backend's ``__init__``
        :return: None
        """
        self.config[backend_name or qual_name] = {'class': qual_name, 'options': options}

    def init_backend(self, qual_name, options):
        """Really initialize the backend

        :param qual_name:
        :param options:
        :return: backend object
        :raise: ImportError
        """
        try:
            module_path, class_name = qual_name.rsplit('.', 1)
        except AttributeError:
            raise WrongBackendError("Invalid backend specification: %r" % qual_name)
        except ValueError:
            module_path, class_name = 'yzcache.backends.%s' % qual_name, None

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
        """

        :return: Backend
        """
        return self[self._default_backend]

    def set_default_backend(self, backend):
        """

        :param backend: string
        :return: None
        """
        self._default_backend = backend

    default_backend = property(get_default_backend, set_default_backend)


backend_manager = BackendManager()
