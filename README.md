YzCache: The Cache Made Easy
============================

YzCache is a library which provides a memoize-like syntax for caching functions and methods.

Syntax:

    @yzcache.cached_function
    def func(x, y):
        return x + y

    >>> func(1, 2)
    3

    >>> func.make_key(1, 2)
    __main__.func(x=1,y=2)

    >>> func.__func__  # raw; methods will need self|cls
    >>> func.val(1, 2)  # direct value, bypass cache
    >>> func.get(1, 2)  # get value only if cached; sort of `exists` test
    >>> func.reset(1, 2)  # reset cached value
    >>> func.unset(1, 2)  # erase cached value


### Groups

Support for groups via `CachedResult` wrapper:

    @cached_group('group_format')
    @cached_function(**cache_params)
    def some_func(arg, kwarg=None):
        return arg ** (kwarg or 1)

`cached_group` detects that it wraps a `cached_function` (more exactly, a `CachedFunction` object)

some_func => CachedFunction


### TODO
* support for descriptors / class.__call__
* @yzcache.cache_groups(*args)
* raise NotCacheable / return NotCacheable