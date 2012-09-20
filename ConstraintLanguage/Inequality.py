import pyparsing as PYP

import Core
import ComponentExpression
reload(Core)
reload(ComponentExpression)


class InequalityAbsNode(object):
    def __init__(self, toks):
        self.quant = toks[0]
        self.ref = toks[1]
        self.operator = toks[2]
        self.op = Core.OperatorEval[toks[2]]
        self.act = toks[3]
        
        
    def initialize(self, Model):
        self.ref = self.ref.initialize(Model)
        if self.quant=='All':
            self.func = self.All
        elif self.quant=='Some':
            self.func = self.Some

    def All(self, Assignment):
        for p in self.ref:
            if not self.op(Assignment[p], self.act):
                return False
        return True

    def Some(self, Assignment):
        for p in self.ref:
            if self.op(Assignment[p], self.act):
                return True
        return False

    def used_variables(self):
        return set(self.ref)
        
    def __call__(self, Assignment):
        return self.func(Assignment)

    def __repr__(self):
        return self.quant+str(self.ref)+self.operator+str(self.act)

class InequalityRelNode(object):
    def __init__(self, toks):
        self.quant = toks[0]
        self.refleft = toks[1]
        self.operator = toks[2]
        self.op = Core.OperatorEval[toks[2]]
        self.refright = toks[3]
        
    def initialize(self, Model):
        self.refleft = self.refleft.initialize(Model)
        self.refright = self.refright.initialize(Model)
                
        if self.quant=='All':
            self.func = self.All
        elif self.quant=='Some':
            self.func = self.Some

    def All(self, Assignment):
        for p1 in self.refleft:
            for p2 in self.refright:
                if not self.op(Assignment[p1], Assignment[p2]):
                    return False
        return True

    def Some(self, Assignment):
        for p1 in self.refleft:
            for p2 in self.refright:
                if self.op(Assignment[p1], Assignment[p2]):
                    return True
        return False

    def used_variables(self):
        return set(self.refleft).union(set(self.refright))
    
    def __call__(self, Assignment):
        return self.func(Assignment)

    def __repr__(self):
        return self.quant+str(self.refleft)+self.operator+str(self.refright)



Quantifier = PYP.CaselessLiteral('All') | PYP.CaselessLiteral('Some')

InequalityAbs = Quantifier + PYP.Suppress('(') + ComponentExpression.ParamReference + Core.Operator + Core.Activity + PYP.Suppress(')')
InequalityAbs.setParseAction(InequalityAbsNode)
InequalityRel = Quantifier + PYP.Suppress('(') + ComponentExpression.ParamReference + Core.Operator + ComponentExpression.ParamReference + PYP.Suppress(')')
InequalityRel.setParseAction(InequalityRelNode)
