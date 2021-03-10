from __future__ import annotations

from .arginfo import arginfo
from .cache import DictCachingKeyLookup
from .cache import LruCachingKeyLookup
from .context import DispatchMethod
from .context import clean_dispatch_methods
from .context import dispatch_method
from .context import methodify

# flake8: noqa
from .dispatch import Dispatch
from .dispatch import LookupEntry
from .dispatch import dispatch
from .error import RegistrationError
from .predicate import ClassIndex
from .predicate import KeyIndex
from .predicate import Predicate
from .predicate import PredicateRegistry
from .predicate import match_class
from .predicate import match_instance
from .predicate import match_key


def make_tree():
    """ show a directory of the project; requires the tree library"""
    import subprocess

    test = subprocess.run(["which", "tree"], stdout=-1, stderr=-1, text=True)
    if test.returncode == 0 and bool(test.stdout):
        tree = subprocess.getoutput(f"/usr/local/bin/tree -n {os.path.dirname(__file__)}")
        sys.stdout.write(tree)
