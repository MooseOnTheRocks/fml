from .parser import *


class Tag:
    def __init__(self, name, props=None, kwprops=None, body=None):
        self.name = name
        self.props = [] if props is None else [*props]
        self.kwprops = {} if kwprops is None else {**kwprops}
        self.body = None if body is None else [*body]

    def __repr__(self):
        return f"Tag({self.name}, {self.props}, {self.kwprops}, {self.body}))"


class Template:
    def __init__(self, name, param_names, bodyparam_name, body):
        self.name = name
        self.param_names = param_names
        self.bodyparam_name = bodyparam_name
        self.body = body
    
    def __repr__(self):
        return f"Template({self.name}, {self.param_names}, ...{self.bodyparam_name}, {self.body})"


class TemplateCall:
    def __init__(self, name, args, body):
        self.name = name
        self.args = args
        self.body = body
        print(f"{str(self)}")
    
    def __repr__(self):
        return f"TemplateCall({self.name}, {self.args} {self.body})"


class Text:
    def __init__(self, text):
        self.text = text
    
    def __repr__(self):
        return f'Text("{self.text}")'


class Var:
    def __init__(self, name):
        self.name = name
    
    def __repr__(self):
        return f"Var({self.name})"


class ParamList:
    def __init__(self, params, kwparams):
        self.params = params
        self.kwparams = kwparams



alpha = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
numeric = "123456789"
symbolic = "-_"

ws = -many(match(*" \n\t\r"))

def p_expr():
    return p_call() | p_var_name() | p_tag() | p_text()

def p_func_def():
    def map_params(p_names):
        return [param[1] for param in p_names if param[0] == "param"]

    def map_bodyparam(p_names):
        res = [param[1] for param in p_names if param[0] == "bodyparam"]
        if len(res) == 0:
            return None
        return res[0]
    
    p = -match("#") << p_name() << ws << p_def_param_list() << ws << p_body()
    return p.map(lambda d: [
        Template(name=d[0],
        param_names=map_params(d[1:-1]),
        bodyparam_name=map_bodyparam(d[1:-1]),
        body=d[-1][1:]
    )])

def p_tag():
    def p(s):
        name_s, name_r = p_name()(s)
        if name_s is None: return None, []
        param_s, param_r = (ws << opt(p_param_list()) << ws)(name_s)
        body_s, body_r = (ws << p_body())(param_s)
        if body_r[0][0] == "none":
            body = None
        else:
            body = body_r[0][1:]
        params = [d[1] for d in param_r if d[0] == "param"]
        kwparams = {d[1]: d[2] for d in param_r if d[0] == "kwparam"}
        return body_s, [Tag(name=name_r[0], props=params, kwprops=kwparams, body=body)]
    return p

def p_call():
    def p(s):
        name_s, name_r = p_var_name().map(lambda n: [n[0].name])(s)
        if name_s is None: return None, []
        param_s, param_r = (ws << p_paren_list(p_name() | p_text()))(name_s)
        if param_s is None: return None, []
        body_s, body_r = (ws << p_body())(param_s)
        if body_s is None: return None, []
        return body_s, [TemplateCall(name_r[0], param_r, body_r[0][1:])]
    return Parser(p)

def p_name():
    return join(match(*alpha, *symbolic) << many(match(*alpha, *numeric, *symbolic)))

def p_text():
    def p(s):
        index = 0
        for c in s:
            if c == '"':
                break
            index += 1
        return s[index:], [s[:index]]
    return (-match('"') << p << -match('"')).map(lambda s: [Text(s[0])])

def p_var_name():
    return -match("$") << p_name().map(lambda n: [Var(n[0])])

def p_def_param_list():
    p = p_param().map(lambda a: [["param", *a]])
    p_last = p_bodyparam().map(lambda b: [["bodyparam", *b]])
    s = ws << -opt(match(",")) << ws
    return -match("(") << ws << opt(sep(p, s)) << ws << opt(-opt(s) << p_last) << ws << -match(")")

def p_paren_list(p):
    s = ws << -opt(match(",")) << ws
    return -match("(") << ws << opt(sep(p, s)) << ws << -match(")")

def p_param_list():
    p = p_kwparam().map(lambda p: [["kwparam", *p]]) |  p_param().map(lambda p: [["param", *p]])
    s = ws << -opt(match(",")) << ws
    last = (-match("...") << ws << p_name()).map(lambda b: [["bparam", *b]]).debug(lambda x: print(f"Got bparam={x}"))
    return -match("(") << ws << opt(sep(p, s) << opt(ws << last)) << ws << -match(")")

def p_param():
    return p_name() | p_var_name() | p_text()

def p_kwparam():
    return p_name() << ws << -match("=") << ws << (p_name() | p_var_name() | p_text())

def p_bodyparam():
    return -match("...") << ws << p_name()

def p_body():
    empty = p_body_empty().map(lambda _: [["empty"]])
    block = p_body_block().map(lambda b: [["block", *b]])
    single = p_body_single().map(lambda s: [["single", *s]])
    none = success([["none"]])
    return single | block | empty | none

def p_body_empty():
    return -match("{") << ws << -match("}")

def p_body_block():
    return -match("{") << ws << many1((p_expr()) << ws) << ws << -match("}")

def p_body_single():
    return -match(":") << ws << p_expr()
