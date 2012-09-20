import pyparsing as PYP
import constraint as CP

import Core
reload(Core)

def ArgsToDict(Function, Variables):
    def closure(*args):
        Assignment = dict(zip(Variables, args))
        return Function(Assignment)
    return closure


class ArithmeticNode(object):
    def __init__(self, toks):
        self.src = toks[0]
        self.op = Core.OperatorEval[toks[1]]
        self.tgt = toks[2]
        
    def initialize(self, Model):
        if not isinstance(self.src, int):
            self.src = self.src.initialize(Model)
        if not isinstance(self.tgt, int):
            self.tgt = self.tgt.initialize(Model)
        

    def __call__(self, Assignment):
        if isinstance(self.src, int):
            left = self.src
        else:
            left = Assignment[self.src]
        if isinstance(self.tgt, int):
            right = self.tgt
        else:
            right = Assignment[self.tgt]
            
        return self.op(left, right)

class FormulaNode(object):
    def __init__(self, toks):
        self.formula = toks[0]

    def initialize(self, Model):
        self.formula.initialize(Model)
        self.model = Model

    def __call__(self, Assignment):
        return self.formula(Assignment)

class ParamReferenceNode(object):
    def __init__(self, toks):
        self.formula = toks[0]
        self.comp = toks[1]
        
    def initialize(self, Model):
        self.formula.initialize(Model)
        self.comp = self.comp.initialize(Model)

        Contexts = self.comp.contexts
        Components = Model.components
        
        prob = CP.Problem()
        params = []
        func = self.formula
        for con in Contexts:
            
            for comp in Components:
                domain = list(con.intervals.get(comp, range(comp.max+1)))
                prob.addVariable(comp.index, domain)

            prob.addConstraint(CP.FunctionConstraint(ArgsToDict(func,Components)), Components)

            if prob.getSolution():
                params.append(con)
                
            prob.reset()

        self.params = params
        return params

Operand = Core.Activity | Core.Component
Arithmetic = Operand + Core.Operator + Operand
Arithmetic.setParseAction(ArithmeticNode)

Formula = PYP.operatorPrecedence(Arithmetic, [(Core.Not, 1, PYP.opAssoc.RIGHT, Core.NotNode),
                                              (Core.And,  2, PYP.opAssoc.LEFT, Core.AndNode),
                                              (Core.Or, 2, PYP.opAssoc.LEFT, Core.OrNode),
                                              (Core.Implies, 2, PYP.opAssoc.LEFT, Core.ImpliesNode)])
Formula.setParseAction(FormulaNode)

ParamReference = Formula + PYP.Suppress('[') + Core.Component + PYP.Suppress(']')
ParamReference.setParseAction(ParamReferenceNode)


