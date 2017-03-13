import pyparsing as PYP
import NiemeyerSolver as CPS


import Basics
reload(Basics)


class BooleanNode(object):
    def __init__(self, toks):
        self.formula = toks[0]
        self.comp = toks[1]
        
    def initialize(self, Model):
        self.formula.initialize(Model)
        self.comp = self.comp.initialize(Model)


        prob = CPS.Problem()
        self.ones = []
        self.zeros = []
        for p in self.comp.parameters:

            for comp in Model.components:
                domain = list(p.context.get(comp, range(comp.max+1)))
                prob.addVariable(comp, domain)
            prob.addConstraint(CPS.FunctionConstraint(Basics.FuncWrapper(self.formula, Model.components)), Model.components)

            if prob.getSolution():
                self.ones.append(p)
            else:
                self.zeros.append(p)
            prob.reset()

    def used_variables(self):
        return set(self.comp.parameters)

    def addConstraints(self, Solver):
        if self.zeros:
            Solver.add(CPS.InSetConstraint([0]), self.zeros)
        if self.ones:
            Solver.add(CPS.InSetConstraint([1]), self.ones)

    def toSQL(self):
        return ' and '.join([str(p)+'=1' for p in self.ones]+[str(p)+'=0' for p in self.zeros])
    
    def __repr__(self):
        return 'Boolean(1:['+']0:['.join([  ','.join([str(p) for p in self.ones]),   ','.join([str(p) for p in self.zeros])  ])+'])'

    def __call__(self, Assignment):
        for p in self.ones:
            if not Assignment[p]==1:
                return False
        for p in self.zeros:
            if not Assignment[p]==0:
                return False
        return True


Grammar = PYP.Suppress(PYP.CaselessLiteral('Boolean(')) + Basics.ParametersFormula + PYP.Suppress(',')  + Basics.Component + PYP.Suppress(')')
Grammar.setParseAction(BooleanNode)
