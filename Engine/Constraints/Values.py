import pyparsing as PYP
import NiemeyerSolver as CPS

import Basics
reload(Basics)

class IneqNode(object):
    def __init__(self, s, l, toks):
        self.s = s
        self.quant = toks[0]
        self.parameters = toks[1]
        self.operator = toks[2]
        self.op = Basics.OperatorEval[toks[2]]
        self.act = toks[3]

        
        
    def initialize(self, Model):
        self.parameters = self.parameters.initialize(Model)
        if self.quant=='All':
            self.call = self.All
        elif self.quant=='Some':
            self.call = self.Some

    def addConstraints(self, Solver):
        if self.quant=='All':
            for p in self.parameters:
                activities = tuple([i for i in p.range if self.op(i,self.act)])
                Solver.add(CPS.InSetConstraint(activities), [p])
        elif self.quant=='Some':
            domain = set([])
            for p in self.parameters:
                activities = set([i for i in p.range if self.op(i,self.act)])
                domain.update(activities)
            Solver.add(CPS.SomeInSetConstraint(domain), self.parameters)
                

    def All(self, Assignment):
        for p in self.parameters:
            if not self.op(Assignment[p], self.act):
                return False
        return True

    def Some(self, Assignment):
        for p in self.parameters:
            if self.op(Assignment[p], self.act):
                return True
        return False

    def used_variables(self):
        return set(self.parameters)

    def toSQL(self):
        if self.quant=='Some':
            con = ' or '
        elif self.quant=='All':
            con = ' and '

        return con.join([str(p)+self.operator+str(self.act) for p in self.parameters])
        
    def __call__(self, Assignment):
        return self.call(Assignment)

    def __repr__(self):
        return self.quant+'('+','.join([str(p) for p in self.parameters])+self.operator+str(self.act)+')'

class InSetNode(object):
    def __init__(self, toks):
        self.quantifier = toks[0]
        self.parameters = toks[1]
        self.set = set(toks[2:])

    def initialize(self, Model):
        self.parameters = self.parameters.initialize(Model)
        if len(self.parameters)==1:
            self.quantifier = 'All'

        if self.quantifier=='All':
            self.call = self.All
        elif self.quantifier=='Some':
            self.call = self.Some

    def used_variables(self):
        return set(self.parameters)

    def addConstraints(self, Solver):
        if self.parameters:
            if self.quantifier=='All':
                for p in self.parameters:
                    Solver.add(CPS.InSetConstraint(self.set), [p])
            elif self.quantifier=='Some':
                Solver.add(CPS.SomeInSetConstraint(self.set), self.parameters)

    def Some(self, Assignment):
        for p in self.parameters:
            if Assignment[p] in self.set:
                return True
        return False

    def All(self, Assignment):
        for p in self.parameters:
            if not Assignment[p] in self.set:
                return False
        return True

    def toSQL(self):
        if self.quantifier=='Some':
            con = ' or '
        elif self.quantifier=='All':
            con = ' and '

        return con.join([str(p)+' in ('+','.join([str(i) for i in self.set])+')' for p in self.parameters])

    def __call__(self, Assignment):
        return self.call(Assignment)

    def __repr__(self):
        return self.quantifier+'InSet('+','.join([str(p) for p in self.parameters])+',{'+','.join([str(i) for i in sorted(self.set)])+'})'

class EqualNode(object):
    def __init__(self, s, l, toks):
        self.s = s
        self.type = toks[0]
        self.parameters = toks[1]
        
    def initialize(self, Model):
        self.parameters = self.parameters.initialize(Model)
        if len(self.parameters)<2:
            raise Exception("Please remove '%s', it references only '%s'."%(self.s, self.parameters))

    def used_variables(self):
        return set(self.parameters)

    def toSQL(self):
        if self.type[:3]=='All':
            con=' and '
        elif self.type[:4]=='Some':
            con=' or '
        eqs = []
        p1 = self.parameters[0]
        for p2 in self.parameters[1:]:
            eqs.append(str(p1)+'='+str(p2))
        return con.join(eqs)

    def __repr__(self):
        return self.type+','.join([str(p) for p in self.parameters])+')'
    

class AllEqNode(EqualNode):
    def __call__(self, Assignment):
        for p1,p2 in zip(self.parameters[:-1], self.parameters[1:]):
            if Assignment[p1]!=Assignment[p2]:
                return False
        return True

    def addConstraints(self, Solver):
        if self.parameters:
            Solver.add(CPS.AllEqualConstraint(), self.parameters)

class SomeEqNode(EqualNode):
    def addConstraints(self, Solver):
        if self.parameters:
            Solver.add(CPS.FunctionConstraint(Basics.FuncWrapper(self.__call__, self.parameters)), self.parameters)

    def __call__(self, Assignment):
        if not self.parameters:
            return True
        
        for p1 in self.parameters:
            for p2 in self.parameters:
                if p1!=p2 and Assignment[p1]==Assignment[p2]:
                    return True
        return False

Quantifier = PYP.CaselessLiteral('All') | PYP.CaselessLiteral('Some')

InSet = Quantifier + PYP.Suppress(PYP.CaselessLiteral('InSet')) + PYP.Suppress('(') + Basics.Parameters + PYP.Suppress(',') + PYP.Suppress('{') + PYP.delimitedList(Basics.Activity) + PYP.Suppress('}') + PYP.Suppress(')')
InSet.setParseAction(InSetNode)
AllEq = PYP.CaselessLiteral('AllEqual(') + Basics.Parameters + PYP.Suppress(')')
AllEq.setParseAction(AllEqNode)
SomeEq = PYP.CaselessLiteral('SomeEqual(') + Basics.Parameters + PYP.Suppress(')')
SomeEq.setParseAction(SomeEqNode)
Ineq = Quantifier + PYP.Suppress('(') + Basics.Parameters + PYP.Suppress(',') + Basics.Operator + PYP.Suppress(',') + Basics.Activity + PYP.Suppress(')')
Ineq.setParseAction(IneqNode)



