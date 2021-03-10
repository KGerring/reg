from __future__ import annotations

from reg import dispatch
from reg import dispatch_method

"Sample module for testing autodoc."


class Foo(object):
    "Class for foo objects."

    @dispatch_method("obj")
    def bar(self, obj):
        "Return the bar of an object."
        return "default"

    def baz(self, obj):
        "Return the baz of an object."


@dispatch("obj")
def foo(obj):
    "return the foo of an object."
    return "default"
