

import pyparsing as PYP
import itertools as IT
import operator


ops = {'=':  operator.eq,
       '>':  operator.gt,
       '<':  operator.lt,
       '>=': operator.ge,
       '<=': operator.le,
       '!=': operator.ne}


class BoolBase(object):
    def __len__(self):
        return len(str(self))


class BoolLiteral(BoolBase):
    def __init__(self, t):
        self.args   = t
        self.name   = t[0]
        self.op     = ops[t[1]]
        self.val    = int(t[2])
    def __str__(self):
        return ''.join(self.args)
    def __call__(self, assignment):
        return self.op(assignment[self.name],self.val)
    def variables(self):
        return set([self.args[0]])

class BoolOperand(BoolBase):
    def __init__(self,t):
        self.args = t[0][0::2]
    def __str__(self):
        sep = " %s " % self.reprsymbol
        return "(" + sep.join(map(str,self.args)) + ")"
    def variables(self):
        v=set([])
        for a in self.args:
            v.update(a.variables())
        return v
    
class BoolAnd(BoolOperand):
    reprsymbol = '&'
    def __call__(self, assignment):
        for a in self.args:
            if not a(assignment):
                return False
        return True

class BoolOr(BoolOperand):
    reprsymbol = '|'    
    def __call__(self, assignment):
        for a in self.args:
            if a(assignment):
                return True
        return False

class BoolNot(BoolOperand):
    def __init__(self, t):
        self.arg = t[0][1]
    def __str__(self):
        return "!" + str(self.arg)
    def __call__(self, assignment):
        return not self.arg(assignment)
    def variables(self):
        return self.arg.variables()

class BoolConstant(BoolBase):
    def __init__(self, s):
        if s == '1':
            self.val = True
        elif s == '0':
            self.val = False
        else:
            print 'Constant equal to',s,'?'
            raise Exception
    def __str__(self):
        return str(int(self.val))
    def __call__(self, assignment):
        return self.val
    def variables(self):
        return set([])
        
        
            
#+'-*[]'
boolLiteral = PYP.Word(PYP.alphanums+'_-/.') + PYP.oneOf("= > < >= <=") + PYP.oneOf(list(PYP.nums))
boolLiteral.setParseAction(BoolLiteral)
boolExpr    = PYP.operatorPrecedence( boolLiteral,
    [
    ("!", 1, PYP.opAssoc.RIGHT, BoolNot),
    ("&", 2, PYP.opAssoc.LEFT,  BoolAnd),
    ("|",  2, PYP.opAssoc.LEFT,  BoolOr),
    ])

def parse( Equation ):
    if Equation in '01':
        return BoolConstant(Equation)
    
    try:
        res = boolExpr.parseString(Equation, parseAll=True)[0]
    except PYP.ParseException, err:
        print err.line
        print " "*(err.column-1) + "^"
        print err

    return res




def test():

    t           = 'u=1 & v=1 | w=0'
    t           = '((u=0 | (u=1 & v=0))) & !(u=2)'
    assignment  = {'u':0,'v':1,'w':0}

    res = parse(t)
    print res
    print res(assignment)
    

if __name__=='__main__':
    test()
