""" Functional Markup Language (FML) """

from .tags import *

# fml files are composed of tags.
# Tags have a name, an optional list/dictionary of attributes, and an optional body.
# Tag by name only (example: br)
#   name
# Tag with attributes (listed and named)
#   name (attr, attrnamed=value)
# Tag with body
#   name { ... }
# Tag with attributes and body
#   name (attr, attrnamed=value) { ... }
# Use double quotes to emit text instead of a name.
# Tag with string as body
#   name { "Hello, World!" }
# Shorthand for a single tag in the body
#   name "Hello, World!"
# or,
#   name span (id="input") { "hi" }



def make_tag(name, props=None, kwprops=None):
    def inner(*body):
        return Tag(name, props, kwprops, body if len(body) > 0 else None)
    return inner

def _lone(name):
    return make_tag(name)

def _tag(name):
    def inner(props=None, kwprops=None, **kwargs):
        all_kwprops = {} if kwprops is None else kwprops
        all_kwprops.update(kwargs)
        return make_tag(name, props, all_kwprops)
    return inner

html = _tag("html")
body = _tag("body")
head = _tag("head")
title = _tag("title")
h1 = _tag("h1")
p = _tag("p")
br = _lone("br")

TAG_NAMES = [
    "html",
    "head",
    "body",
    "title",
    "p",
    "br",
    "h1"
]


