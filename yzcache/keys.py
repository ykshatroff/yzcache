# -*- coding: utf-8 -*-
# Date: 22.11.15
from __future__ import unicode_literals

import inspect


def get_qualname(obj):
    if isinstance(obj, basestring):
        return obj
    if inspect.ismodule(obj):
        spec = obj.__name__,
    elif inspect.isclass(obj):
        spec = obj.__module__, obj.__name__
    elif inspect.isfunction(obj):
        spec = getattr(obj, '__qualname__', None) or (obj.__module__, obj.__name__)
    elif inspect.ismethod(obj):
        owner_class = inspect.isclass(obj.im_self) and obj.im_self or obj.im_class
        spec = owner_class.__module__, owner_class.__name__, obj.im_func.__name__
    else:
        cls = type(obj)
        spec = cls.__module__, cls.__name__
    return '.'.join(spec)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
