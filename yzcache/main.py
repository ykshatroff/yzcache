# -*- coding: utf-8 -*-
# Date: 22.11.15
from __future__ import unicode_literals
import copy
import weakref
from inspect import getcallargs, ismethod, isclass
from yzcache.keys import get_qualname

cache = weakref.WeakValueDictionary()
cache_to = []


class CachedResult(object):
    def __init__(self, result):
        self.result = result


class CachedFunction(object):
    """A class which functions as a function wrapper and method descriptor

    """
    def __init__(self, func, args_to_str=None):
        # TODO callable objects?
        if ismethod(func):
            # cases like CachedFunction(obj.method)
            self.__self__ = func.__self__
            self.im_class = isclass(func.__self__) and func.__self__ or func.im_class
            func = func.__func__
        else:
            # otherwise at init time we don't know the real `self` and class
            self.__self__ = None
            self.im_class = None

        if isinstance(func, (classmethod, staticmethod)):
            # we don't need original class/static method objects
            # use what's needed and let them be GC'ed
            self._method = type(func)
            func = func.__func__
        else:
            self._method = None

        self.__func__ = func  # the real callable function
        self.__module__ = func.__module__
        self.__doc__ = func.__doc__
        self.__name__ = func.__name__

    @property
    def im_self(self):
        return self.__self__

    @property
    def im_func(self):
        return self.__func__

    def __call__(self, *args, **kwargs):
        """Perform lookup into cache or the real function call

        :param args:
        :param kwargs:
        :return:
        """
        func = self.__func__
        callargs = self._make_args(*args, **kwargs)
        key = self._make_key(callargs)
        val = cache.get(key)
        if val is None:
            val = func(**callargs)
            res = CachedResult(val)
            cache[key] = res
            cache_to.append(res)  # TODO: timeout
            # self._status = 'cached'
        else:
            val = val.result
        return val

    def __get__(self, instance, owner=None):
        if owner is None:
            owner = type(instance)

        if instance is not None or (self.im_class is not None and self.im_class is not owner):
            # create copy of self:
            # - always for an instance method
            # - if caller class differs from original class
            new_self = copy.copy(self)
            new_self.__self__ = instance
            new_self.im_class = owner
            return new_self

        self.im_class = owner
        return self

    def _make_args(self, *args, **kwargs):
        func = self.__func__
        instance = self.__self__
        if self._method:
            method = self._method
            owner = self.im_class
            # a class/static method
            if owner is None:
                owner = type(instance)
            if method is classmethod:
                # print "Testing: classmethod %s.%s" % (owner.__name__, func.__name__)
                args = (owner, ) + tuple(args)
            elif method is staticmethod:
                # print "Testing: staticmethod %s.%s" % (owner.__name__, func.__name__)
                pass
        elif instance is not None:
            # an instance method: append instance in front of args
            args = (instance, ) + tuple(args)
        else:
            # a simple function
            pass

        return getcallargs(func, *args, **kwargs)

    def _make_key(self, args):
        """

        :param args: the dict of final callargs
        :return: str
        """
        func = self.__func__
        owner = self.im_class
        if owner:
            spec = get_qualname(owner) + "." + func.__name__
        else:
            spec = get_qualname(func)
        if args:
            s = []
            for k in sorted(args.keys()):
                v = args[k]
                s.append('{0}={1!r}'.format(k, v))
            spec += '({0})'.format(','.join(s))
        else:
            spec += '()'
        return spec


def cached_function(f=None):
    if f is None:
        return lambda f: cached_function(f)

    return CachedFunction(f)
