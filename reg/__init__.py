# flake8: noqa
from .dispatch import dispatch, Dispatch, LookupEntry
from .context import (dispatch_method, DispatchMethod,
                      methodify, clean_dispatch_methods)
from .arginfo import arginfo
from .error import RegistrationError
from .predicate import (Predicate, KeyIndex, ClassIndex,
                        match_key, match_instance, match_class, PredicateRegistry)
from .cache import DictCachingKeyLookup, LruCachingKeyLookup

def make_tree():
    """ show a directory of the project; requires the tree library"""
    import subprocess
    
    test = subprocess.run(["which", "tree"], stdout=-1, stderr=-1, text=True)
    if test.returncode == 0 and bool(test.stdout):
        tree = subprocess.getoutput(
                f"/usr/local/bin/tree -n {os.path.dirname(__file__)}"
        )
        sys.stdout.write(tree)
