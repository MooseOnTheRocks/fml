from multiprocessing.sharedctypes import Value
from optparse import Values


class Result:
    def __init__(self, rem=None, value=None, fail_msg=None, trace=None, *, success):
        self.success = success
        self.rem = rem
        self.value = value
        self.fail_msg = fail_msg
        self.trace = [] if trace is None else [*trace]
    
    @property
    def failed(self): return not self.success


class Failure(Result):
    def __init__(self, rem, fail_msg, **kwargs):
        super().__init__(rem=rem, fail_msg=fail_msg, **kwargs, success=False)
    
    def __repr__(self):
        return f"Failure<{self.fail_msg}, rem={self.rem}>"
    

class Success(Result):
    def __init__(self, rem, value, **kwargs):
        super().__init__(rem=rem, value=value, **kwargs, success=True)
    
    def __repr__(self):
        return f"Success<{self.value}, rem={self.rem}>"


class Parser:
    def __init__(self, pfunc, name=None):
        self.pfunc = pfunc
        self.name = name

    def debug(self, f):
        def p(s):
            r_s, r_r = self(s)
            f(r_r)
            return r_s, r_r
        return Parser(p)
    
    def trace(self, desc):
        def p(s):
            sa, ra = self(s)
            ra.trace.append(desc)
            return sa, ra
        return Parser(p)
    
    def set_msg(self, msg):
        def p(s):
            sa, ra = self(s)
            ra.msg = msg
            return sa, ra
        return Parser(p)
    
    def map(self, f):
        def p(s):
            sa, ra = self(s)
            if sa is None:
                return sa, ra
            return sa, f(ra)
        return Parser(p)
    
    def __neg__(self):
        def p(s):
            sa, _ = self(s)
            return sa, []
        
        return Parser(p)
    
    def __ror__(self, other):
        return self | other

    def __or__(self, other):
        if not callable(other):
            raise TypeError(f"Parser | on: {type(other)}")
        
        def p(s):
            sa, ra = self(s)
            if sa is not None: return sa, ra
            sb, rb = other(s)
            if sb is not None: return sb, rb
            return None, []
        return Parser(p)
    
    def __rlshift__(self, other):
        return self << other
    
    def __lshift__(self, other):
        if not callable(other):
            raise TypeError(f"Parser << on: {type(other)}")
        
        def p(s):
            sa, ra = self(s)
            if sa is None: return None, []
            sb, rb = other(sa)
            if sb is None: return None, []
            return sb, [*ra, *rb]

        return Parser(p)

    def __call__(self, s):
        return self.pfunc(s)

# == Parsers

def match(*ws):
    def p(s):
        for w in ws:
            check = s[:len(w)]
            if check == w:
                return s[len(w):], [w]
        return None, []
    return Parser(p)

def opt(q):
    def p(s):
        ss, r = q(s)
        if ss is None:
            return s, []
        return ss, r
    return Parser(p)

def success(val):
    def p(s):
        return s, val
    return Parser(p)

def many(q):
    def p(s):
        ss, rr = q(s)
        if ss is None:
            return s, []
        return (success(rr) << many(q))(ss)
    return Parser(p)

def join(q):
    def p(s):
        ss, rr = q(s)
        return ss, ["".join(rr)]
    return Parser(p)

def many1(q):
    return q << many(q)

def sep(p, s):
    return p << many(s << p)
