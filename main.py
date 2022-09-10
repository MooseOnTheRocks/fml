from fml.parser import *
from fml.funcs import *
from fml.tags import *


def eval_call(tc, context, templates):
    if tc.name not in templates:
        raise KeyError(f"No template named {tc.name}")
    
    template = templates[tc.name]
    call_args = tc.args
    # call_body = tc.body

    if len(call_args) != len(template.param_names):
        raise ValueError(f"Template expects {len(template.param_names)} arguments, received {len(call_args)}")
    
    params = dict(zip(template.param_names, call_args))
    if template.bodyparam_name is not None:
        print(f"{template.bodyparam_name=}")
        print(f"{tc.body=}")
        ebs = []
        for t in tc.body:
            print(f"PARSE CALL BODY: {t}")
            evs = eval_any(t, {**context}, templates)
            print(f"PARSED RES: {evs}")
            ebs.append(evs)
        params[template.bodyparam_name] = ebs


    
    print(f"Eval call params: {params}")
    print(f"Template: {template}")

    evals = []
    for t in template.body:
        print(f"Template t: {t=}")
        ta = eval_any(t, {**context, **params}, templates)
        print(f"{ta=}")
        evals.extend(ta)
    
    print(f"{evals=}")
    return evals


def eval_tag(tag, context, templates):
    name = tag.name
    params = None
    kwparams = None
    body = None

    if tag.body is not None:
        body = []
        for t in tag.body:
            body.extend(eval_any(t, context, templates))
        # body = [eval_any(t, context, templates) for t in tag.body]
    
    if tag.props is not None:
        params = []
        for p in tag.props:
            if isinstance(p, Var):
                params.append(context[p.name])
            else:
                params.append(p)
    
    if tag.kwprops is not None:
        kwparams = {}
        for k, v in tag.kwprops.items():
            if isinstance(v, Var):
                kwparams[k] = context[v.name]
            else:
                kwparams[k] = v
    
    return [Tag(name, params, kwparams, body)]

def eval_any(obj, context, templates):
    if isinstance(obj, TemplateCall):
        return eval_call(obj, context, templates)
    elif isinstance(obj, Tag):
        return eval_tag(obj, context, templates)
    elif isinstance(obj, Text):
        return [obj.text]
    elif isinstance(obj, str):
        return [obj]
    elif isinstance(obj, Var):
        print(f"{obj=}")
        return eval_any(context[obj.name], context, templates)
    elif isinstance(obj, list):
        evals = []
        for o in obj:
            evals.extend(eval_any(o, context, templates))
        return evals
    else:
        raise TypeError(f"Cannot eval object: {obj!r}")

def eval_fml(parsed_fml):
    templates = {}
    stmts = []

    for obj in parsed_fml:
        if isinstance(obj, Template):
            templates[obj.name] = obj
        else:
            stmts.append(obj)
    
    evals = []
    for stmt in stmts:
        evals.extend(eval_any(stmt, {}, {**templates}))
    
    return evals, templates

def parse_fml():
    top_level = p_func_def() | p_tag()
    return many((ws << top_level << ws))

def emit_tag(tag):
    if isinstance(tag, str):
        return tag
    
    ss = f"<{tag.name}"
    for p in tag.props:
        if isinstance(p, Text):
            ss += f' "{p.text}"'
        else:
            ss += p
    for k, v in tag.kwprops.items():
        ss += f" {k}="
        if isinstance(v, Text):
            ss += f'"{v.text}"'
        else:
            ss += f"{v}"
    ss += ">"

    if tag.body is not None:
        ss += "\n"
        ems = []
        for t in tag.body:
            ems.append(emit_tag(t))
        ss += "\n".join(ems)
        if len(ems) != 0:
            ss += "\n"
        ss += f"</{tag.name}>"
    
    return ss



if __name__ == "__main__":
    with open("index.fml") as file:
        source = file.read()
    
    rem, tags = parse_fml()(source)

    print("== Rem")
    print(f"{rem!r}")
    print()

    print("== Tags")
    # print(tags)
    for tag in tags:
        print(tag)
    print()

    print("== Eval")
    evals, templates = eval_fml(tags)
    print(f"{templates=}")
    print(f"{evals=}")

    as_html = "\n".join(map(emit_tag, evals))

    print(as_html)
    with open("index.html", "w") as file:
        file.write(as_html)
    
