import pyparsing as PYP
import NiemeyerSolver as CPS


import Values
import Basics
reload(Values)
reload(Basics)


class MultiplexNode(object):
    def __init__(self, s, l, toks):
        self.s = s
        self.formulas = toks[:-1]
        self.comp = toks[-1]
        
    def initialize(self, Model):
        for f in self.formulas:
            f.initialize(Model)
        self.comp = self.comp.initialize(Model)

        prob = CPS.Problem()
        classes = {}
        for p in self.comp.parameters:
            
            Id = []
            for func in self.formulas:
                for comp in Model.components:
                    domain = list(p.context.get(comp, range(comp.max+1)))
                    prob.addVariable(comp, domain)
                prob.addConstraint(CPS.FunctionConstraint(Basics.FuncWrapper(func, Model.components)), Model.components)

                if prob.getSolution():
                    Id.append(True)
                else:
                    Id.append(False)
                prob.reset()
                
            Id = tuple(Id)
            if Id in classes:
                classes[Id].append(p)
            else:
                classes[Id]=[p]

        self.classes = [tuple(c) for c in classes.values() if len(c)>1]
        if not self.classes:
            raise Exception("'%s' defines only empty classes, please remove."%self.s)
        self.parameters = set([p for c in classes.values() for p in c])

    def used_variables(self):
        return self.parameters

    def addConstraints(self, Solver):
        for c in self.classes:
            Solver.add(CPS.AllEqualConstraint(), c)

    def toSQL(self):
        eqs = []
        for c in self.classes:
            p1 = c[0]
            for p2 in c[1:]:
                eqs.append(str(p1)+'='+str(p2))
        return ' and '.join(eqs)
    
    def __repr__(self):
        return 'Multiplex('+','.join(['='.join([str(p) for p in c]) for c in self.classes])+')'

    def __call__(self, Assignment):
        for c in self.classes:
            p1 = c[0]
            for p2 in c[1:]:
                if not Assignment[p1]==Assignment[p2]:
                    return False
        return True


Grammar = PYP.Suppress(PYP.CaselessLiteral('Multiplex(')) + PYP.delimitedList(Basics.ParametersFormula) + PYP.Suppress(',')  + Basics.Component + PYP.Suppress(')')
Grammar.setParseAction(MultiplexNode)
