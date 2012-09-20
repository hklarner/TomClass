import pyparsing as PYP
import constraint as CP

import ComponentExpression
import Core
reload(ComponentExpression)
reload(Core)


class MultiplexNode(object):
    def __init__(self, toks):
        self.formulas = toks[:-1]
        self.comp = toks[-1]
        
    def initialize(self, Model):
        for f in self.formulas:
            f.initialize(Model)
        self.comp = self.comp.initialize(Model)

        Contexts = self.comp.contexts
        Components = Model.components

        def ArgsToDict(Function, Variables):
            def closure(*args):
                Assignment = dict(zip(Variables, args))
                return Function(Assignment)
            return closure
        
        prob = CP.Problem()
        classes = {}
        for con in Contexts:
            
            vector = []
            for func in self.formulas:
                for comp in Components:
                    domain = list(con.intervals.get(comp, range(comp.max+1)))
                    prob.addVariable(comp.index, domain)
                prob.addConstraint(CP.FunctionConstraint(ArgsToDict(func, Components)), Components)

                if prob.getSolution():
                    vector.append(True)
                else:
                    vector.append(False)
                prob.reset()
            vector = tuple(vector)

            if vector in classes:
                classes[vector].append(con)
            else:
                classes[vector]=[con]

        self.classes = [tuple(c) for c in classes.values() if len(c)>1]
        print self

    def used_variables(self):
        s=set([])
        for c in self.classes:
            s.update(set(c))
        return s
    
    def __repr__(self):
        return 'Multiplex: '+' + '.join(['='.join([str(p) for p in c]) for c in self.classes])

    def __call__(self, Assignment):
        for c in self.classes:
            p1 = c[0]
            for p2 in c[1:]:
                if not Assignment[p1]==Assignment[p2]:
                    return False
        return True


Multiplex = PYP.Suppress(PYP.CaselessLiteral('Multiplex(')) + PYP.delimitedList(ComponentExpression.Formula) + PYP.Suppress('[')  + Core.Component + PYP.Suppress(']') + PYP.Suppress(')')
Multiplex.setParseAction(MultiplexNode)
