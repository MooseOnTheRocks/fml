from asyncio import ALL_COMPLETED
from pkgutil import ImpImporter
from fml.parser import *
from fml.funcs import *
from fml.tags import *

ALL_TESTS = []

def test(*sources):
    def wrapper(f):
        def inner(*args, **kwargs):
            f_name = f.__name__
            arg_strs = map(str, args)
            kw_strs = [f"{k}={v}" for k, v in kwargs.items()]
            param_str = ", ".join([*arg_strs, *kw_strs])
            print(f"=== Test :: {f_name}({param_str})")

            p = f(*args, **kwargs)
            for source in sources:
                print(f"{source=}")
                s, r = (ws << p << ws)(source)
                print(f"{s=}")
                print(f"{r=}")
                print()
        ALL_TESTS.append(inner)
        return inner
    return wrapper

@test("some-name")
def test_name():
    return p_name()

@test("$special")
def test_var_name():
    return p_var_name()

@test('"a string my guy"')
def test_text():
    return p_text()

@test('defer')
def test_param():
    return p_name()

@test('id="no"')
def test_kwparam():
    return p_kwparam()

@test('(id="no", class="yes", defer)')
def test_param_list():
    return p_param_list()

@test(
    "$func(id)",
    '$func(defer, id) {p: "Hello" br p: "Sup"}',
    "$func()"
)
def test_call():
    return p_call()

@test("""
html {
    head(id="classy") {
        title(defer): "Hi there!"
    }
}
""")
def test_tag():
    return p_tag()

@test("""
#pretty(x) {
    b: i: $x
}
""")
def test_def():
    return p_func_def()

if __name__ == "__main__":
    for i, t in enumerate(ALL_TESTS):
        t()
