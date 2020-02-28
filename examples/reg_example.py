# thirdparty

__VERBOSE__ = True

import reg
from reg import methodify

if __VERBOSE__:
    from ansimarkup import ansiprint
else:
    def ansiprint(*args, **kwargs): return


def cprint(result):
    if not __VERBOSE__:
        return
    else:
        from ansimarkup import ansiprint
        ansiprint(f'res:<c>\t{result!r}</c>')

def vprint(s):
    if not __VERBOSE__:
        return
    else:
        print(s)

class Document(object):
    def __init__(self, text):
        self.text = text

    def size(self):
        return len(self.text)


class Folder(object):
    def __init__(self, entries):
        self.entries = entries

    def size(self):
        return sum([entry.size() for entry in self.entries])


class Image(object):
    def __init__(self, bytes):
        self.bytes = bytes

    def size(self):
        return len(self.bytes)


def document_size(item):
    return len(item.text)


def folder_size(item):
    return sum([document_size(entry) for entry in item.entries])


del folder_size


def folder_size(item):
    return sum([size(entry) for entry in item.entries])


def image_size(item):
    return len(item.bytes)


def size(item):
    if isinstance(item, Document):
        return document_size(item)
    elif isinstance(item, Image):
        return image_size(item)
    elif isinstance(item, Folder):
        return folder_size(item)
    assert False, "Unknown item: %s" % item


size_function_registry = {
    Document: document_size,
    Image: image_size,
    Folder: folder_size,
}


def register_size(class_, function):
    size_function_registry[class_] = function


def size(item):
    return size_function_registry[item.__class__](item)


class File(object):
    def __init__(self, bytes):
        self.bytes = bytes


def file_size(item):
    return len(item.bytes)


### register it
register_size(File, file_size)

# What if we introduce a new HtmlDocument item that is a subclass of Document?
class HtmlDocument(Document):
    pass  # imagine new html functionality here


# We need to remember to also call register_size for HtmlDocument. We can reuse document_size:
register_size(HtmlDocument, document_size)

##########
##########


#### using reg #####


def size(item):
    raise NotImplementedError


# This function raises NotImplementedError as we don't know how to get the size for an arbitrary Python object. Not very useful yet. We need to be able to hook the actual implementations into it. To do this, we first need to transform the size function to a generic one:

it = reg.dispatch("my_item")

size = reg.dispatch("item")(size)
#### OR as a deco ####


@reg.dispatch("item")
def size(item):
    raise NotImplementedError
    # What this says that when we call size, we want to dispatch based on the class of its item argument.


size.register(document_size, item=Document)
size.register(folder_size, item=Folder)
size.register(image_size, item=Image)
size.register(file_size, item=File)


class Request(object):
    def __init__(self, request_method="GET", body=""):
        self.request_method = request_method
        self.body = body


# We've also defined a body attribute which contains text in case the request is a POST request.
# We use the previously defined Document as the model class.
# Now we define a view function that dispatches on the `class` of the model instance, and the `request_method` attribute of the request:


@reg.dispatch(
    reg.match_instance("obj"),
    reg.match_key("request_method", lambda obj, request: request.request_method),
)
def view(obj, request):
    raise NotImplementedError


### As you can see here we use match_instance and match_key instead of strings to specify how to dispatch.
# If you use a string argument, this string names an argument and dispatch is based on the `class` of the `instance` you pass in.
# Here we use `match_instance`, which is equivalent to this:
# we have a `obj` predicate which uses the `class` of the obj argument for dispatch.

# We also use `match_key`, which dispatches on the request_method `attribute` of the request;
# this attribute is a string, so dispatch is on string matching, not `isinstance` as with `match_instance`.
# You can use any Python immutable with `match_key`, not just strings.


@view.register(request_method="GET", obj=Document)
def document_get(obj, request):
    return "Document text is: " + obj.text


@view.register(request_method="POST", obj=Document)
def document_post(obj, request):
    obj.text = request.body
    return "We changed the document"


@view.register(request_method="GET", obj=Image)
def image_get(obj, request):
    return obj.bytes


@view.register(request_method="POST", obj=Image)
def image_post(obj, request):
    obj.bytes = request.body
    return "We changed the image"


_doc = doc = Document("Hello World")
image = Image("abc")
htmldoc = HtmlDocument("abc")


ansiprint('<C><k> testing view functions</k></C>')
vprint("""view(doc, Request('GET'))""")
res = view(_doc, Request("GET"))
cprint(res)

res = view(_doc, Request("POST", "New content"))
vprint("""view(doc, Request('POST', 'New content'))""")
cprint(res)
ansiprint('<g>#######################</g>')
vprint("""doc.text""")
_doc.text
ansiprint(f"<b>result: {doc.text}</b>")

#u; \x1b[34ma\x1b[0m
#\x1b[34;4m{}\x1b[0m

#print('\x1b[106;30m{}\x1b[0m')
ansiprint('<g>#######################</g>')

vprint("""view(image, Request('GET'))""")
res = view(image, Request("GET"))
cprint(res)

res = view(image, Request("POST", "new data"))
vprint("""view(image, Request('POST', "new data"))""")
cprint(res)


ansiprint('<C><k> showing its the same etc; ln 209 </k></C>')
vprint("""image.bytes""")
ansiprint(f"<red>result: {image.bytes!r}</red>")
image.bytes


# Rather than having a size function and a view function, we can also have a context class with size and view as methods.
class CMS(object):
    @reg.dispatch_method("item")
    def size(self, item):
        raise NotImplementedError

    @reg.dispatch_method(
        reg.match_instance("obj"),
        reg.match_key(
            "request_method", lambda self, obj, request: request.request_method
        ),
    )
    def view(self, obj, request):
        return "Generic content of {} bytes.".format(self.size(obj))


@CMS.size.register(item=Document)
def document_size_as_method(self, item):
    return len(item.text)


#### using it without the context arg to turn the func into a method for reg


CMS.size.register(methodify(folder_size), item=Folder)
CMS.size.register(methodify(image_size), item=Image)
CMS.size.register(methodify(file_size), item=File)

ansiprint('<b> testing `cms=CMS()` example <b>')

cms = CMS()
vprint("""cms.size(Image("123"))""")
res = cms.size(Image("123"))
cprint(res)


vprint("""cms.size(Document("12345"))""")
res = cms.size(Document("12345"))
cprint(res)


@CMS.view.register(request_method="GET", obj=Document)
def document_get(self, obj, request):
    return "{}-byte-long text is: {}".format(self.size(obj), obj.text)

ansiprint('<C><k> testing cms.view.register stuff </k></C>')

res0 = cms.view(Document("12345"), Request("GET"))
res1 = cms.view(Image("123"), Request("GET"))
vprint("""
cms.view(Document("12345"), Request("GET"))
cms.view(Image("123"), Request("GET"))
""")
cprint(res0)
cprint(res1)

#### You can look up the implementation that a generic function would dispatch to without calling it.
size.by_args(_doc).component
size.by_predicates(item=Document).component
view.by_predicates(request_method="GET", obj=Document).key
view.by_predicates(obj=Image, request_method="POST").key

size.by_args(_doc).component is size.by_args(htmldoc).component
size.by_args(_doc).all_matches
size.by_args(htmldoc).all_matches


def htmldocument_size(doc):
    return len(doc.text) + 1  # 1 so we can see a difference


size.register(htmldocument_size, item=HtmlDocument)
size.by_args(htmldoc).all_matches

# The implementation are listed in order of `decreasing` specificity, with the first one as the one returned by the `component` attribute:
######

#### Service Discovery https://reg.readthedocs.io/en/latest/patterns.html#service-discovery
# Here we’ve created a generic function that takes no arguments (and thus does no dynamic dispatch). But you can still plug its actual implementation into the registry from elsewhere:

@reg.dispatch()
def emailer():
    raise NotImplementedError

sent = []

def send_email(sender, subject, body):
    # some specific way to send email
    sent.append((sender, subject, body))

def actual_emailer():
    return send_email

emailer.register(actual_emailer)
the_emailer = emailer()
the_emailer('someone@example.com', 'Hello', 'hello world!')


#####

@reg.dispatch(reg.match_class('cls'))
def something(cls):
    raise NotImplementedError()

def something_for_object(cls):
    return "Something for %s" % cls
something.register(something_for_object, cls=object)

class DemoClass(object):
    pass

class ParticularClass(DemoClass):
    pass
def something_particular(cls):
    return "Particular for %s" % cls

something.register(
    something_particular,
    cls=ParticularClass)

REGISTERED = ['emailer', 'size', 'something', 'view', 'CMS']

def get_caller_module_dict(levels = 1):
    f = sys._getframe(levels)
    ldict = f.f_globals.copy()
    if f.f_globals != f.f_locals:
        ldict.update(f.f_locals)
    return ldict

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

view.add_predicates([
    reg.match_instance('model', get_model, model_fallback),
    reg.match_key('name', get_name, name_fallback),
    reg.match_key('request_method', get_request_method, request_method_fallback)
])

def foo_default(self, request):
    return "foo default"

def foo_post(self, request):
    return "foo default post"

def foo_edit(self, request):
    return "foo edit"

register_value(view, (Foo, '', 'GET'), foo_default)
register_value(view, (Foo, '', 'POST'), foo_post)
register_value(view, (Foo, 'edit', 'POST'), foo_edit)

key_lookup = view.key_lookup
assert key_lookup.component((Foo, '', 'GET')) is foo_default
assert key_lookup.component((Foo, '', 'POST')) is foo_post
assert key_lookup.component((Foo, 'edit', 'POST')) is foo_edit
assert key_lookup.component((FooSub, '', 'GET')) is foo_default
assert key_lookup.component((FooSub, '', 'POST')) is foo_post

class Request(object):
    def __init__(self, name, request_method):
        self.name = name
        self.request_method = request_method

assert view(
    Foo(), Request('', 'GET')) == 'foo default'
assert view(
    FooSub(), Request('', 'GET')) == 'foo default'
assert view(
    FooSub(), Request('edit', 'POST')) == 'foo edit'

class Bar(object):
    pass

assert view(
    Bar(), Request('', 'GET')) == 'Model fallback'
assert view(
    Foo(), Request('dummy', 'GET')) == 'Name fallback'
assert view(
    Foo(), Request('', 'PUT')) == 'Request method fallback'
assert view(
    FooSub(), Request('dummy', 'GET')) == 'Name fallback'

def get_caching_key_lookup(r):
    return reg.DictCachingKeyLookup(r)






if __name__ == "__main__":
    print(__name__)
