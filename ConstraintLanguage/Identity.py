import pyparsing as PYP

import ComponentExpression
reload(ComponentExpression)

class IdentityNode(object):
    def __init__(self, toks):
        self.quant = toks[0]
        self.ref = toks[1]
        
    def initialize(self, Model):
        self.ref = self.ref.initialize(Model)
        if len(self.ref)<2:
            self.ref = []
            self.func = lambda x: True
        elif self.quant == 'All':
            self.func = self.All
        elif self.quant == 'Some':
            self.func = self.Some

    def used_variables(self):
        return set(self.ref)

    def All(self, Assignment):
        for p1,p2 in zip(self.ref[:-1], self.ref[1:]):
            if Assignment[p1]!=Assignment[p2]:
                return False
        return True

    def Some(self, Assignment):
        for p1 in self.ref:
            for p2 in self.ref:
                if p1!=p2 and Assignment[p1]==Assignment[p2]:
                    return True
        return False


    def __repr__(self):
        return self.quant+'Identical'+str(self.ref)
    
    def __call__(self, Assignment):
        return self.func(Assignment)

Quantifier = PYP.CaselessLiteral('All') | PYP.CaselessLiteral('Some')
Identity = Quantifier + PYP.Suppress(PYP.CaselessLiteral('Identical(')) + ComponentExpression.ParamReference + PYP.Suppress(')')
Identity.setParseAction(IdentityNode)
