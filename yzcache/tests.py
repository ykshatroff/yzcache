# -*- coding: utf-8 -*-
# Date: 22.11.15
from __future__ import unicode_literals

import unittest
from yzcache.keys import get_qualname
from yzcache.main import cached_function, cache


class UtilsTest(unittest.TestCase):
    def test_basic(self):
        def f():
            pass

        class Desc(object):
            def __get__(self, obj, instance=None):
                pass

        class A(object):
            desc = Desc()

            def im(self):
                pass

            @classmethod
            def cm(cls):
                pass

            @staticmethod
            def sm():
                pass

        # assignment to class makes f a method
        A.f = f
        a = A()
        # assignment to instance doesn't make f a method
        a.ff = f

        self.assertEqual(get_qualname(f), 'yzcache.tests.f')
        self.assertEqual(get_qualname(A), 'yzcache.tests.A')
        self.assertEqual(get_qualname(a), 'yzcache.tests.A')

        self.assertEqual(get_qualname(A.cm), 'yzcache.tests.A.cm')
        self.assertEqual(get_qualname(a.cm), 'yzcache.tests.A.cm')

        self.assertEqual(get_qualname(A.sm), 'yzcache.tests.sm')
        self.assertEqual(get_qualname(A.im), 'yzcache.tests.A.im')
        self.assertEqual(get_qualname(a.im), 'yzcache.tests.A.im')
        self.assertEqual(get_qualname(A.f), 'yzcache.tests.A.f')
        self.assertEqual(get_qualname(a.f), 'yzcache.tests.A.f')
        self.assertEqual(get_qualname(a.ff), 'yzcache.tests.f')


class CacheTest(unittest.TestCase):
    def test_basic(self):
        def f1():
            return 10

        f3 = cached_function(f1)
        self.assertEqual(f3(), f1())

        @cached_function
        def f2():
            return 10

        self.assertEqual(f2.__name__, 'f2')
        self.assertEqual(f2(), 10)

    def test_callargs(self):
        def f1(a, b=5, c=10):
            return a + b + c
        f3 = cached_function(f1)

        self.assertEqual(f3._make_args(1), {'a': 1, 'b': 5, 'c': 10})

    def test_keys(self):
        class A(object):
            x = 9

            def __init__(self, x):
                self.x = x

            @cached_function
            def get_x(self):
                return self.x

        a = A(15)
        args = a.get_x._make_args()
        self.assertEqual(args, {'self': a})
        self.assertEqual(a.get_x._make_key(args), 'yzcache.tests.A.get_x(self={!r})'.format(a))

    def test_cached_method(self):
        class A(object):
            x = 9

            def __init__(self, x):
                self.x = x

            @cached_function
            def get_x(self):
                return self.x

            @cached_function
            @classmethod
            def get_class_x(cls):
                return cls.x

            def outside(self, a, b=5):
                return self.x + a + b

        class B(A):
            x = 8

        a = A(15)
        self.assertEqual(a.get_x(), 15)
        self.assertEqual(a.get_class_x(), 9)
        self.assertEqual(B.get_class_x(), 8)

        outside = cached_function(a.outside)
        self.assertEqual(outside(1), 21)

        counter = {}
        test_fn = lambda: counter.update({'n': counter.get('n', 0) + 1})
        test_fn_cached = cached_function(test_fn)
        key = test_fn_cached._make_key({})
        self.assertEqual(key, 'yzcache.tests.<lambda>()')

        cache.clear()
        test_fn_cached()
        self.assertEqual(len(cache), 1)
        self.assertIn(key, cache)
        test_fn_cached()
        self.assertEqual(counter['n'], 1)
