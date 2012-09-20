import pyparsing as PYP
import operator as OP



class ComponentNode(object):
    def __init__(self, toks):
        self.arg = toks[0]

    def initialize(self, Model):
        for comp in Model.components:
            if self.arg==comp.name:
                return comp
        raise Exception('Unknown component %s'%self.arg)

class ImpliesNode(object):
    def __init__(self, toks):
        self.a = toks[0][0]
        self.b = toks[0][2]

    def initialize(self, Model):
        self.a.initialize(Model)
        self.b.initialize(Model)

    def used_variables(self):
        s = self.a.used_variables()
        s.update(self.b.used_variables())
        return s

    def __repr__(self):
        return '('+str(self.a)+' => '+str(self.b)+')'

    def __call__(self, Assignment):
        if not self.a(Assignment):
            return True
        return self.b(Assignment)
        
class AndNode(object):
    def __init__(self, toks):
        self.args = toks[0][::2]
        
    def initialize(self, Model):
        for a in self.args:
            a.initialize(Model)

    def used_variables(self):
        s = set([])
        for a in self.args:
            s.update(a.used_variables())
        return s
            
    def __call__(self, Assignment):
        for a in self.args:
            if not a(Assignment):
                return False
        return True

    def __repr__(self):
        return '('+' and\n'.join([str(a) for a in self.args])+')'

class OrNode(object):
    def __init__(self, toks):
        self.args = toks[0][::2]
        
    def initialize(self, Model):
        for a in self.args:
            a.initialize(Model)

    def used_variables(self):
        s = set([])
        for a in self.args:
            s.update(a.used_variables())
        return s
    
    def __call__(self, Assignment):
        for a in self.args:
            if a(Assignment):
                return True
        return False
    
    def __repr__(self):
        return '('+' or\n'.join([str(a) for a in self.args])+')'

class NotNode(object):
    def __init__(self, toks):
        self.arg = toks[0][1]
        
    def initialize(self, Model):
        self.arg.initialize(Model)

    def used_variables(self):            
        return self.arg.used_variables()
        
    def __call__(self, Assignment):
        if not self.arg(Assignment):
            return True
        return False
    
    def __repr__(self):
        return '('+'not ' + str(self.arg)+')'


OperatorEval = {'=': OP.eq,'>': OP.gt,'>=': OP.ge,'<': OP.lt,'<=': OP.le,'!=': OP.ne}
Activities = ['0','1','2','3','4','5','6','7','8','9']
Operators = ['<','<=','=','>=','>','!=']
Operator = PYP.oneOf(Operators)

And = PYP.CaselessKeyword('and')
Not = PYP.CaselessKeyword('not')
Or = PYP.CaselessKeyword('or')
Implies = PYP.Literal('=>')

Activity = PYP.oneOf(Activities)
Activity.setParseAction(lambda x: int(x[0]))

Component = PYP.Word(PYP.alphas, PYP.alphanums, 1)
Component.setParseAction(ComponentNode)


