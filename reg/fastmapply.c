#include <Python.h>

static PyObject*
lookup_mapply(PyObject *self, PyObject *args, PyObject* kwargs)
{
  PyObject* callable_obj;
  PyObject* lookup_obj;
  PyObject* remaining_args;
  PyObject* func_obj;
  PyObject* result;
  PyCodeObject* co;
  PyObject* method_obj = NULL;
  int i, has_lookup = 0, cleanup_dict = 0;

  if (PyTuple_GET_SIZE(args) < 2) {
    PyErr_SetString(PyExc_TypeError,
                    "lookup_mapply() takes at least two parameters");
    return NULL;
  }

  callable_obj = PyTuple_GET_ITEM(args, 0);
  lookup_obj = PyTuple_GET_ITEM(args, 1);
  remaining_args = PyTuple_GetSlice(args, 2, PyTuple_GET_SIZE(args));

  if (!PyCallable_Check(callable_obj)) {
    PyErr_SetString(PyExc_TypeError,
                    "first parameter must be callable");
    return NULL;
  }

  if (PyFunction_Check(callable_obj)) {
    /* function */
    func_obj = callable_obj;
  } else if (PyMethod_Check(callable_obj)) {
    /* method */
    func_obj = PyMethod_Function(callable_obj);
  } else if (PyType_Check(callable_obj)) {
    /* new style class */
    method_obj = PyObject_GetAttrString(callable_obj, "__init__");
    if (PyMethod_Check(method_obj)) {
      func_obj = PyMethod_Function(method_obj);
    } else {
      /* descriptor found, not method, so no __init__ */
      method_obj = NULL;
      /* we are done immediately, just call type */
      goto final;
    }
  } else if (PyClass_Check(callable_obj)) {
    /* old style class */
    method_obj = PyObject_GetAttrString(callable_obj, "__init__");
    if (method_obj != NULL) {
      func_obj = PyMethod_Function(method_obj);
    } else {
      PyErr_SetString(PyExc_TypeError,
                      "Old-style class without __init__ not supported");
      return NULL;
    }
  } else if (PyCFunction_Check(callable_obj)) {
    /* function implemented in C extension */
    PyErr_SetString(PyExc_TypeError,
                    "functions implemented in C are not supported");
    return NULL;
  } else {
    /* new or old style class instance */
    method_obj = PyObject_GetAttrString(callable_obj, "__call__");
    if (method_obj != NULL) {
      func_obj = PyMethod_Function(method_obj);
    } else {
      PyErr_SetString(PyExc_TypeError,
                      "Instance is not callable");
      return NULL;
    }
  }

  /* we can determine the arguments now */
  co = (PyCodeObject*)PyFunction_GetCode(func_obj);

  if (!(co->co_flags & CO_VARKEYWORDS)) {
    for (i = 0; i < co->co_argcount; i++) {
      PyObject* name = PyTuple_GET_ITEM(co->co_varnames, i);
      if (strcmp(PyString_AS_STRING(name), "lookup") == 0) {
        has_lookup = 1;
        break;
      }
    }
    if (has_lookup) {
      if (kwargs == NULL) {
        kwargs = PyDict_New();
        cleanup_dict = 1;
      }
      PyDict_SetItem(kwargs, PyString_FromString("lookup"), lookup_obj);
    }
  }
 final:
  result = PyObject_Call(callable_obj, remaining_args, kwargs);
  Py_DECREF(remaining_args);
  if (cleanup_dict) {
    Py_DECREF(kwargs);
  }
  Py_XDECREF(method_obj);
  return result;
}

static PyMethodDef FastMapplyMethods[] = {
  {"lookup_mapply", (PyCFunction)lookup_mapply, METH_VARARGS | METH_KEYWORDS,
   "apply with optional lookup parameter"},
  {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC
initfastmapply(void)
{
  (void) Py_InitModule("fastmapply", FastMapplyMethods);
}