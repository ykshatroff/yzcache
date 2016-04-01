# -*- coding: utf-8 -*-
# Date: 22.11.15
from __future__ import absolute_import, unicode_literals
import copy
from inspect import getcallargs, ismethod, isclass, isfunction, isgeneratorfunction
from .keys import get_qualname
from .backends import backend_manager


class CachedResult(object):
    def __init__(self, result):
        self.result = result


class CachedFunction(object):
    """A class which functions as a function wrapper and method descriptor

    """
    backend = None

    def __init__(self, func, args_to_str=None, backend=None, cache_default=CachedResult):
        self.cache = backend_manager.backends[backend]

        # TODO cache callable objects?
        if not isfunction(func):
            if isinstance(func, (classmethod, staticmethod)):
                # we don't need original class/static method objects
                # use what's needed and let them be GC'ed
                self._method = type(func)
                self.__self__ = None
            elif ismethod(func):
                # cases like CachedFunction(obj.method)
                self._method = None
                self.__self__ = func.__self__
            else:
                raise TypeError("Don't know how to handle %r" % func)
            func = func.__func__

        if isgeneratorfunction(func):
            raise TypeError("Don't know how to handle generator function %r" % func)

        self.__func__ = func  # the real callable function
        self.__module__ = func.__module__
        self.__doc__ = func.__doc__
        self.__name__ = func.__name__
        self.cache_default = cache_default

    @property
    def im_self(self):
        return self.__self__

    @property
    def im_func(self):
        return self.__func__

    def __getattr__(self, item):
        return getattr(self.__func__, item)

    def __call__(self, *args, **kwargs):
        """Perform lookup into cache or the real function call

        :param args:
        :param kwargs:
        :return:
        """
        func = self.__func__
        callargs = self._make_args(*args, **kwargs)
        key = self._make_key(callargs)
        val = self.cache.get(key, self.cache_default)
        if val is self.cache_default:
            val = func(**callargs)
            res = CachedResult(val)
            self.cache[key] = res
            # self._status = 'cached'
        else:
            val = val.result
        return val

    def __get__(self, instance, owner=None):
        """Descriptor method

        If ``instance`` is None, we're like an unbound or static method of class ``owner``
        If ``instance`` is a class, we're like a classmethod, ``owner`` is a ``<type 'type'>``
        If ``instance`` is an instance, we're like an instance method of class ``owner``

        :param instance: None | class | instance
        :param owner: None | class | type
        :return: CachedFunction
        """
        try:
            if self._method is staticmethod:
                try:
                    self.im_class
                except AttributeError:
                    # get the class where the method is originally defined
                    for cls in owner.__mro__:
                        if cls.__dict__.get(self.__name__) == self:
                            self.im_class = owner
                            break
                    else:
                        self.im_class = owner
                return self
        except AttributeError:
            pass
        if owner is None:
            owner = type(instance)

        try:
            im_class = self.im_class
        except AttributeError:
            self.im_class = im_class = owner

        if instance is not None or im_class is not owner:
            # create copy of self:
            # - always for an instance method
            # - if caller class differs from original class
            new_self = copy.copy(self)
            new_self.__self__ = instance
            new_self.im_class = owner
            return new_self

        return self

    def _make_args(self, *args, **kwargs):
        func = self.__func__
        try:
            instance = self.__self__
        except AttributeError:
            # a generic function
            pass
        else:
            method = getattr(self, '_method', None)
            # class/static method via __get__
            if method:
                if method is classmethod:
                    owner = getattr(self, 'im_class', type(instance))
                    args = (owner, ) + tuple(args)
            # instance method via __get__
            elif instance is not None:
                args = (instance, ) + tuple(args)
            else:
                # [usually, this is the case of unbound methods]
                # instance is expected to be supplied as args[0]
                pass

        return getcallargs(func, *args, **kwargs)

    def _make_key(self, args):
        """

        :param args: the dict of final callargs
        :return: str
        """
        func = self.__func__
        try:
            owner = self.im_class
        except AttributeError:
            spec = get_qualname(func)
        else:
            spec = get_qualname(owner) + "." + func.__name__
        if args:
            s = ['{0}={1!r}'.format(k, v)
                 for k, v in sorted(args.items())]
            spec += '({0})'.format(','.join(s))
        else:
            spec += '()'
        return spec

    def flush(self, *args, **kwargs):
        call_args = self._make_args(*args, **kwargs)
        key = self._make_key(call_args)
        self.cache.delete(key)


def cached_function(f=None):
    """The decorator

    :param f:
    :type f: function|classmethod|staticmethod
    :return: CachedFunction
    """
    if f is None:
        return lambda f: cached_function(f)

    return CachedFunction(f)
