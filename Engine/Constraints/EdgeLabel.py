import pyparsing as PYP
import operator as OP
import NiemeyerSolver as CPS

import Basics
reload(Basics)



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

DisjSQL = {'Activating': '>',
           'ActivatingOnly': '>',
           'Inhibiting': '<',
           'InhibitingOnly': '<',
           'Observable': '!='}
ConjSQL = {'ActivatingOnly': '>=',
           'InhibitingOnly': '<=',
           'NotObservable': '=',
           'NotActivating': '<=',
           'NotInhibiting': '>='}

class EdgeLabelNode(object):
    def __init__(self, toks):
        self.label = toks[0]
        self.regulator = toks[1]
        self.target = toks[2]
        self.thr = toks[3]
        
        self.formula = False
        if len(toks)==5:
            self.formula = toks[4]
        
    def initialize(self, Model):
        self.regulator = self.regulator.initialize(Model)
        self.target = self.target.initialize(Model)


        accepted=False
        for comp, thrs in self.regulator.targets:
            if comp==self.target:
                if self.thr in thrs:
                    accepted=True
                    break
                
        if not accepted:
            raise Exception('Non-existing threshold %i for interaction %s->%s'%(self.thr, self.regulator, self.target))

        ParsLHS = [p for p in self.target.parameters if self.thr in p.context[self.regulator]]
        ParsRHS = [p for p in self.target.parameters if self.thr-1 in p.context[self.regulator]]

        if self.formula:
            self.formula.initialize(Model)

            prob = CPS.Problem()
            pairs = []
            for p1, p2 in zip(ParsLHS,ParsRHS):
                
                for comp in Model.components:
                    domain = list(p1.context.get(comp, range(comp.max+1)))
                    prob.addVariable(comp.index, domain)

                prob.addConstraint(CPS.FunctionConstraint(Basics.FuncWrapper(self.formula, Model.components)), Model.components)

                if prob.getSolution():
                    pairs.append((p1,p2))
                    
                prob.reset()
            self.pairs = pairs
        else:
            self.pairs = zip(ParsLHS, ParsRHS)

        self.requirements = []
        if self.label in ConjLabelEval:
            self.op_conj = ConjLabelEval[self.label]
            self.requirements.append(self.ConjEval)
        if self.label in DisjLabelEval:
            self.op_disj = DisjLabelEval[self.label]
            self.requirements.append(self.DisjEval)

    def ConjEval(self, Assignment):
        for p1, p2 in self.pairs:
            if not self.op_conj(Assignment[p1], Assignment[p2]):
                return False
        return True

    def DisjEval(self, Assignment):
        for p1, p2 in self.pairs:
            if self.op_disj(Assignment[p1], Assignment[p2]):
                return True
        return False

    def pair_func(self, pair, func):
        def closure(Assignment):
            p1,p2 = pair
            return func(Assignment[p1],Assignment[p2])
        return closure
            
    def used_variables(self):
        s=set([])
        for p in self.pairs:
            s.update(set(p))
        return s

    def addConstraints(self, Solver):
        if self.label in ConjLabelEval:
            parameters = [p for pair in self.pairs for p in pair]
            for pair in self.pairs:
                func = self.pair_func(pair, self.op_conj)
                Solver.add(CPS.FunctionConstraint(Basics.FuncWrapper(func, pair)), pair)
        if self.label in DisjLabelEval:
            parameters = [p for pair in self.pairs for p in pair]
            Solver.add(CPS.FunctionConstraint(Basics.FuncWrapper(self.DisjEval, parameters)), parameters)
        

    def toSQL(self):
        conj = []
        if self.label in ConjSQL:
            op = ConjSQL[self.label]
            conj.extend([str(x)+op+str(y) for x,y in self.pairs])
        if self.label in DisjSQL:
            op = DisjSQL[self.label]
            condition = ' or '.join([str(x)+op+str(y) for x,y in self.pairs])
            if conj:
                condition = '('+condition+')'
            conj.append(condition)

        return ' and '.join(conj)
        
    
    def __call__(self, Assignment):
        for f in self.requirements:
            if not f(Assignment):
                return False
        return True

    def __repr__(self):
        return self.label+':('+str(self.pairs)+')'


Label= PYP.CaselessKeyword('Observable') ^ PYP.CaselessKeyword('NotObservable')\
       ^ PYP.CaselessKeyword('Activating') ^ PYP.CaselessKeyword('NotActivating') ^ PYP.CaselessKeyword('ActivatingOnly')\
       ^ PYP.CaselessKeyword('Inhibiting') ^ PYP.CaselessKeyword('NotInhibiting') ^ PYP.CaselessKeyword('InhibitingOnly')
Grammar = Label + PYP.Suppress('(') + Basics.Component + PYP.Suppress(',') + Basics.Component + PYP.Suppress(',') + Basics.Activity + \
                      PYP.Optional(PYP.Suppress(',') + Basics.ParametersFormula) + PYP.Suppress(')')
Grammar.setParseAction(EdgeLabelNode)




