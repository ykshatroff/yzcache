# -*- coding: utf-8 -*-
# Date: 22.11.15
from __future__ import absolute_import

import inspect
import six


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


def make_key(func, owner=None, args=None, args_to_str=None):
    """Make a cache key for a function (or a method of ``owner``) called with ``args``,
    using a mapping of ``args_to_str`` or ``args_to_str.format(**args)``

    :param func: callable
    :param owner: the class owning a method's definition
    :param args: dict of callargs [actually, OrderedDict]
    :param args_to_str: dict, str
    :return: str
    """
    if owner is None:
        spec = get_qualname(func)
    else:
        spec = get_qualname(owner) + "." + func.__name__
        if args:
            cls_arg_name, cls_arg_value = args.items()[0]  # remove 'cls' argument: if it is the owner class
            if cls_arg_value is owner:
                args = args.copy()
                args.pop(cls_arg_name)
    if args:
        if isinstance(args_to_str, six.string_types):
            formatted = args_to_str and args_to_str.format(**args)
        else:
            s = []
            for k, v in args.items():  # for any given function, callargs has the same keys
                try:
                    coder = args_to_str[k]
                except KeyError:
                    if six.PY2 and isinstance(v, unicode):  # remove `u` in `u''`
                        v = v.encode('utf-8')
                    elif six.PY3 and isinstance(v, (bytes, bytearray)):  # remove `b` in `b''`
                        v = six.text_type(v, encoding='utf-8')
                    v = repr(v)
                else:
                    if coder is None:
                        continue
                    elif isinstance(coder, six.string_types):
                        v = coder.format(k=v)
                    elif callable(coder):
                        v = coder(v)
                    else:
                        raise ValueError("Invalid value type {1!r} for {0!r} argument formatter"
                                         .format(k, type(v).__name__))
                s.append('{0}={1}'.format(k, v))
            formatted = ','.join(s)
        spec += '({0})'.format(formatted)
    else:
        spec += '()'
    return spec


if __name__ == "__main__":
    import doctest
    doctest.testmod()
