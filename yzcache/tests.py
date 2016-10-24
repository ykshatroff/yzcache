# -*- coding: utf-8 -*-
# Date: 22.11.15
from __future__ import unicode_literals

import os
import unittest
from yzcache import backend_manager
from yzcache.backends import BackendManager, Backend
from yzcache.keys import get_qualname
from yzcache.main import cached_function


TEST_SETTINGS = {
    'default': {
        'class': 'dict_backend',
    },
    'other': {
        'class': 'noop',
    }
}


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


class BackendTest(unittest.TestCase):
    def test_single(self):
        os.environ['YZCACHE_SETTINGS'] = 'yzcache.tests.TEST_SETTINGS'
        mgr = BackendManager()
        self.assertIn('default', mgr.config)
        self.assertIsInstance(mgr['default'], Backend)


class CacheTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        backend_manager.add_backend('dict_backend')
        backend_manager.set_default_backend('dict_backend')
        cls.cache = backend_manager['dict_backend']  # used in test_cached_method()

    def test_basic(self):
        def f1():
            return 10

        f3 = cached_function(f1)
        self.assertEqual(f3(), f1())

        @cached_function
        def f2():
            """Test docs"""
            return 10

        self.assertEqual(f2.__name__, 'f2')
        self.assertEqual(f2.__doc__, "Test docs")
        self.assertEqual(f2.__module__, __name__)
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

            @cached_function
            @classmethod
            def get_class_x(cls):
                return cls.x

            @cached_function
            @staticmethod
            def get_static_x():
                return A.x

        class B(A):
            x = 10

        a = A(15)
        args = a.get_x._make_args()
        self.assertEqual(args, {'self': a})
        self.assertEqual(a.get_x._make_key(args), 'yzcache.tests.A.get_x(self={!r})'.format(a))

        args = A.get_class_x._make_args()
        self.assertEqual(A.get_class_x._make_key(args), "yzcache.tests.A.get_class_x()")
        args = a.get_class_x._make_args()
        self.assertEqual(a.get_class_x._make_key(args), "yzcache.tests.A.get_class_x()")
        args = B.get_class_x._make_args()
        self.assertEqual(B.get_class_x._make_key(args), 'yzcache.tests.B.get_class_x()')

        d = a.get_static_x
        args = d._make_args()

        self.assertEqual(a.get_static_x._make_key(args), 'yzcache.tests.A.get_static_x()')

        d = B.get_static_x
        assert d == A.__dict__['get_static_x']
        args = d._make_args()
        self.assertEqual(B.get_static_x._make_key(args), 'yzcache.tests.A.get_static_x()')

    def test_make_key_encode(self):
        @cached_function()
        def _test(arg):
            pass

        self.assertEqual(_test._make_key({'arg': 'asd'}), _test._make_key({'arg': b'asd'}))

    def test_make_key_none(self):
        @cached_function(args_to_str={'arg': None})
        def _test(arg):
            pass

        self.assertEqual(_test._make_key({'arg': 'asd'}), _test._make_key({}))

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

            @cached_function
            @staticmethod
            def get_static_x():
                return A.x

            def outside(self, a, b=5):
                return self.x + a + b

        class B(A):
            x = 8

        a = A(15)
        self.assertEqual(a.get_x(), 15)
        self.assertEqual(a.get_class_x(), 9)
        self.assertEqual(B.get_class_x(), 8)

        with self.assertRaises(TypeError):
            A.get_x()

        self.assertEqual(a.get_static_x(), A.x)
        self.assertEqual(A.get_static_x(), A.x)
        self.assertEqual(B.get_static_x(), A.x)

        outside = cached_function(a.outside)
        self.assertEqual(outside(1), 21)

        counter = {}
        test_fn = lambda: counter.update({'n': counter.get('n', 0) + 1}) or 1
        test_fn_cached = cached_function(test_fn)
        key = test_fn_cached._make_key({})
        self.assertEqual(key, 'yzcache.tests.<lambda>()')

        cache = self.cache
        cache.clear()
        test_fn_cached()
        self.assertEqual(cache.get(key), 1)
        test_fn_cached()
        self.assertEqual(counter['n'], 1)
