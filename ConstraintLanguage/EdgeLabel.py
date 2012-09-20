import pyparsing as PYP
import constraint as CP
import operator as OP

import Core
import ComponentExpression
reload(Core)
reload(ComponentExpression)



def ArgsToDict(Function, Variables):
    def closure(*args):
        Assignment = dict(zip(Variables, args))
        return Function(Assignment)
    return closure

DisjLabelEval = {'Activating': OP.gt,
                 'ActivatingOnly': OP.gt,
                 'Inhibiting': OP.lt,
                 'InhibitingOnly': OP.lt,
                 'Observable': OP.ne}
ConjLabelEval = {'ActivatingOnly': OP.ge,
                 'InhibitingOnly': OP.le,
                 'NotObservable': OP.eq,
                 'NotActivating': OP.le,
                 'NotInhibiting': OP.ge}

class EdgeLabelNode(object):
    def __init__(self, toks):
        self.label = toks[0]
        self.source = toks[1]
        self.target = toks[2]
        self.thr = toks[3]
        
        self.formula = False
        if len(toks)==5:
            self.formula = toks[4]
        
    def initialize(self, Model):
        self.source = self.source.initialize(Model)
        self.target = self.target.initialize(Model)

        accepted=False
        for comp, thrs in self.source.targets:
            if comp==self.target:
                if self.thr in thrs:
                    accepted=True
                    break
        if not accepted:
            raise Exception('Non-existing threshold %i for interaction %s->%s'%(self.thr, self.source, self.target))

        ContextsAbove = [con for con in self.target.contexts if self.thr in con.intervals[self.source]]
        ContextsBelow = [con for con in self.target.contexts if self.thr-1 in con.intervals[self.source]]
        
        if self.formula:
            self.formula.initialize(Model)

            Components = Model.components
            prob = CP.Problem()
            
            pairs = []
            func = self.formula
            for con1, con2 in zip(ContextsAbove,ContextsBelow):
                
                for comp in Components:
                    domain = list(con1.intervals.get(comp, range(comp.max+1)))
                    prob.addVariable(comp.index, domain)

                prob.addConstraint(CP.FunctionConstraint(ArgsToDict(func,Components)), Components)

                if prob.getSolution():
                    pairs.append((con1,con2))
                    
                prob.reset()
            self.pairs = pairs
        else:
            self.pairs = zip(ContextsAbove, ContextsBelow)

        funcs = []
        if self.label in ConjLabelEval:
            self.op_conj = ConjLabelEval[self.label]
            funcs.append(self.ConjEval)
        if self.label in DisjLabelEval:
            self.op_disj = DisjLabelEval[self.label]
            funcs.append(self.DisjEval)
        self.funcs = funcs

    def ConjEval(self, Assignment):
        for p1, p2 in self.pairs:
            if not self.op_conj(Assignment[p1.index], Assignment[p2.index]):
                return False
        return True

    def DisjEval(self, Assignment):
        for p1, p2 in self.pairs:
            if self.op_disj(Assignment[p1.index], Assignment[p2.index]):
                return True
        return False
            
    def used_variables(self):
        s=set([])
        for p in self.pairs:
            s.update(set(p))
        return s
    
    def __call__(self, Assignment):
        return all([f(Assignment) for f in self.funcs])

    def __repr__(self):
        return self.label+': '+str(self.pairs)


Label= PYP.CaselessKeyword('Observable') ^ PYP.CaselessKeyword('NotObservable')\
       ^ PYP.CaselessKeyword('Activating') ^ PYP.CaselessKeyword('NotActivating') ^ PYP.CaselessKeyword('ActivatingOnly')\
       ^ PYP.CaselessKeyword('Inhibiting') ^ PYP.CaselessKeyword('NotInhibiting') ^ PYP.CaselessKeyword('InhibitingOnly')
EdgeLabel = Label + PYP.Suppress('(') + Core.Component + PYP.Suppress(',') + Core.Component + PYP.Suppress(',') + Core.Activity + \
                      PYP.Optional(PYP.Suppress(',') + ComponentExpression.Formula) + PYP.Suppress(')')
EdgeLabel.setParseAction(EdgeLabelNode)




