#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" 
$ 
"""

from __future__ import annotations  # isort:skip
import sys  # isort:skip
import os  # isort:skip

import reg


def register_value(generic, key, value):
    """Low-level function that directly uses the internal registry of the
    generic function to register an implementation.
    """
    generic.register.__self__.registry.register(key, value)


class Foo(object):
    pass


class FooSub(Foo):
    pass


@reg.dispatch()
def view(self, request):
    raise NotImplementedError()


def get_model(self, request):
    return self


def get_name(self, request):
    return request.name


def get_request_method(self, request):
    return request.request_method


def model_fallback(self, request):
    return "Model fallback"


def name_fallback(self, request):
    return "Name fallback"


def request_method_fallback(self, request):
    return "Request method fallback"


view.add_predicates(
    [reg.match_instance("model", get_model, model_fallback), reg.match_key("name", get_name, name_fallback), reg.match_key("request_method", get_request_method, request_method_fallback)]
)


def foo_default(self, request):
    return "foo default"


def foo_post(self, request):
    return "foo default post"


def foo_edit(self, request):
    return "foo edit"


register_value(view, (Foo, "", "GET"), foo_default)
register_value(view, (Foo, "", "POST"), foo_post)
register_value(view, (Foo, "edit", "POST"), foo_edit)

key_lookup = view.key_lookup
assert key_lookup.component((Foo, "", "GET")) is foo_default
assert key_lookup.component((Foo, "", "POST")) is foo_post
assert key_lookup.component((Foo, "edit", "POST")) is foo_edit
assert key_lookup.component((FooSub, "", "GET")) is foo_default
assert key_lookup.component((FooSub, "", "POST")) is foo_post


class Request(object):
    def __init__(self, name, request_method):
        self.name = name
        self.request_method = request_method


assert view(Foo(), Request("", "GET")) == "foo default"
assert view(FooSub(), Request("", "GET")) == "foo default"
assert view(FooSub(), Request("edit", "POST")) == "foo edit"


class Bar(object):
    pass


assert view(Bar(), Request("", "GET")) == "Model fallback"
assert view(Foo(), Request("dummy", "GET")) == "Name fallback"
assert view(Foo(), Request("", "PUT")) == "Request method fallback"
assert view(FooSub(), Request("dummy", "GET")) == "Name fallback"


##############
##############
##############


class DemoClass(object):
    pass


class SpecialClass(object):
    pass


class ClassFoo(object):
    def __repr__(self):
        return "<instance of ClassFoo>"


class ClassBar(object):
    def __repr__(self):
        return "<instance of ClassBar>"


# def test_dispatch_basic():
@reg.dispatch(reg.match_class("cls"))
def something(cls):
    raise NotImplementedError()


def something_for_object(cls):
    return "Something for %s" % cls


something.register(something_for_object, cls=object)
assert something(DemoClass) == ("Something for <class '{}.DemoClass'>".format(__name__))
assert something.by_args(DemoClass).component is something_for_object
assert something.by_args(DemoClass).all_matches == [something_for_object]


# def test_classdispatch_multidispatch():
@reg.dispatch(reg.match_class("cls"), "other")
def something(cls, other):
    raise NotImplementedError()


def something_for_object_and_object(cls, other):
    return "Something, other is object: %s" % other


def something_for_object_and_foo(cls, other):
    return "Something, other is ClassFoo: %s" % other


something.register(something_for_object_and_object, cls=object, other=object)

something.register(something_for_object_and_foo, cls=object, other=ClassFoo)

assert something(DemoClass, ClassBar()) == ("Something, other is object: <instance of ClassBar>")
assert something(DemoClass, ClassFoo()) == ("Something, other is Foo: <instance of ClassFoo>")

############################################################


@reg.dispatch(reg.match_class("cls"))
def something(cls, extra):
    raise NotImplementedError()


def something_for_object(cls, extra):
    return "Extra: %s" % extra


something.register(something_for_object, cls=object)
assert something(DemoClass, "foo") == "Extra: foo"


__all__ = sorted(
    [
        getattr(v, "__name__", k)
        for k, v in list(globals().items())  # export
        if ((callable(v) and getattr(v, "__module__", "") == __name__ or k.isupper()) and not str(getattr(v, "__name__", k)).startswith("__"))  # callables from this module  # or CONSTANTS
    ]
)  # neither marked internal

if __name__ == "__main__":
    print(__file__)
