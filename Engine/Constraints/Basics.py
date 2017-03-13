

import NiemeyerSolver as CPS
import operator as OP
import pyparsing as PYP


OperatorEval = {'=': OP.eq,'>': OP.gt,'>=': OP.ge,'<': OP.lt,'<=': OP.le,'!=': OP.ne}
Activities = ['0','1','2','3','4','5','6','7','8','9']
Operators = ['<','<=','=','>=','>','!=']
Operator = PYP.oneOf(Operators)

And = PYP.CaselessKeyword('and')
Not = PYP.CaselessKeyword('not')
Or = PYP.CaselessKeyword('or')
Implies = PYP.Literal('->')

Activity = PYP.oneOf(Activities)
Activity.setParseAction(lambda x: int(x[0]))



def FuncWrapper(Function, Variables):
    def closure(*args):
        Assignment = dict(zip(Variables, args))
        return Function(Assignment)
    return closure

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
        if not self.a.used_variables():
            raise Exception("Constraint '%s' is empty, cannot compute '=>'."%str(self.a))
        if not self.b.used_variables():
            raise Exception("Constraint '%s' is empty, cannot compute '=>'."%str(self.b))

    def used_variables(self):
        s = self.a.used_variables()
        s.update(self.b.used_variables())
        return s

    def addConstraints(self, Solver):
        parameters = tuple(self.used_variables())
        Solver.add(CPS.FunctionConstraint(FuncWrapper(self.__call__, parameters)), parameters)

    def toSQL(self):
        return '(not (%s) or (%s))'%(self.a.toSQL(), self.b.toSQL())

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
            if not a.used_variables():
                raise Exception("Constraint '%s' is empty, cannot compute 'and'."%str(a))
            s.update(a.used_variables())
        return s

    def addConstraints(self, Solver):
        for a in self.args:
            a.addConstraints(Solver)

    def toSQL(self):
        return ' and '.join(['(%s)'%a.toSQL() for a in self.args])
            
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
            if not a.used_variables():
                raise Exception("Constraint '%s' is empty, cannot compute 'or'."%str(a))
            s.update(a.used_variables())
        return s

    def addConstraints(self, Solver):
        parameters = tuple(self.used_variables())
        Solver.add(CPS.FunctionConstraint(FuncWrapper(self.__call__, parameters)), parameters)

    def toSQL(self):
        return ' or '.join(['(%s)'%a.toSQL() for a in self.args])
    
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
        if not self.arg.used_variables():
            raise Exception("Constraint '%s' is empty, cannot compute 'not'."%str(self.arg))

    def used_variables(self):            
        return self.arg.used_variables()

    def addConstraints(self, Solver):
        parameters = tuple(self.arg.used_variables())
        Solver.add(CPS.FunctionConstraint(FuncWrapper(self.__call__, parameters)), parameters)
            

    def toSQL(self):
        return 'not (%s)'%self.arg.toSQL()
        
    def __call__(self, Assignment):
        if not self.arg(Assignment):
            return True
        return False
    
    def __repr__(self):
        return '('+'not ' + str(self.arg)+')'

class ParametersAtomNode(object):
    def __init__(self, toks):
        self.LHS = toks[0]
        self.op_str = toks[1]
        self.op = OperatorEval[toks[1]]
        self.RHS = toks[2]

        if isinstance(self.RHS, int):
            self.call = self.absolute
        else:
            self.call = self.relative
        
    def initialize(self, Model):
        if not isinstance(self.LHS, int):
            self.LHS = self.LHS.initialize(Model)
        if not isinstance(self.RHS, int):
            self.RHS = self.RHS.initialize(Model)

    def used_variables(self):
        s = set([self.LHS])
        if not isinstance(self.RHS, int):
            s.add(self.RHS)
        return s

    def __call__(self, Assignment):
        return self.call(Assignment)

    def absolute(self, Assignment):
        return self.op(Assignment[self.LHS], self.RHS)

    def relative(self, Assignment):
        return self.op(Assignment[self.LHS], Assignment[self.RHS])

    def addConstraints(self, Solver):
        if isinstance(self.RHS, int):
            domain = tuple([i for i in range(self.LHS.max+1) if self.op(i, self.RHS)])
            Solver.add(CPS.InSetConstraint(domain), [self.LHS])
        else:
            Solver.add(CPS.FunctionConstraint(FuncWrapper(self.relative, [self.LHS, self.RHS])), [self.LHS, self.RHS])
        

    def __repr__(self):
        return str(self.LHS)+self.op_str+str(self.RHS)

class ParametersFormulaNode(object):
    def __init__(self, toks):
        self.formula = toks[0]

    def initialize(self, Model):
        self.formula.initialize(Model)

    def addConstraints(self, Solver):
        self.formula.addConstraints(Solver)

    def used_variables(self):
        return self.formula.used_variables()

    def __call__(self, Assignment):
        return self.formula(Assignment)

    def __repr__(self):
        return str(self.formula)

class ParametersNode(object):
    def __init__(self, toks):
        self.formula = toks[0]
        self.comp = toks[1]
        
    def initialize(self, Model):
        self.formula.initialize(Model)
        self.comp = self.comp.initialize(Model)
        
        prob = CPS.Problem()
        params = []
        func = self.formula
        for p in self.comp.parameters:
            
            for comp in Model.components:
                domain = list(p.context.get(comp, range(comp.max+1)))
                prob.addVariable(comp.index, domain)

            prob.addConstraint(CPS.FunctionConstraint(FuncWrapper(self.formula, Model.components)), Model.components)

            if prob.getSolution():
                params.append(p)
                
            prob.reset()

        if not params:
            raise Exception("Empty parameter reference '%s', please update."%self.formula)

        return params

class KNode(object):
    def __init__(self, toks):
        self.component = toks[0]
        self.activities = toks[1]

    def initialize(self, Model):
        comp = self.component.initialize(Model)

        if len(self.activities)!=len(comp.regulators):
            raise Exception('Error in parameter specification K_%s_%s. %s has %i regulators, not %i.'%(comp, self.activities, comp, len(comp.regulators), len(self.activities)))

        for act, (reg,thrs) in zip(self.activities, comp.regulators):
            if not int(act) in (0,) + thrs:
                raise Exception('Error in parameter specification K_%s_%s. %s is not a threshold of (%s,%s).'%(comp, self.activities, act, reg, comp))
            

        for p in comp.parameters:
            if all([int(act) in p.context[reg] for act, (reg,thrs) in zip(self.activities, comp.regulators)]):
                k = p
                break

        return k

class KFormulaAbsNode(object):
    def __init__(self, toks):
        self.LHS = toks[0]
        self.op_str = toks[1]
        self.op = OperatorEval[toks[1]]
        self.RHS = toks[2]

        if isinstance(self.LHS, int):
            d = self.LHS
            self.LHS = self.RHS
            self.RHS = d

    def initialize(self, Model):
        self.LHS = self.LHS.initialize(Model)

    def toSQL(self):
        return str(self.LHS)+self.op_str+str(self.RHS)

    def used_variables(self):
        return set([self.LHS])

    def addConstraints(self, Solver):
        domain = tuple([i for i in self.LHS.range if self.op(i, self.RHS)])
        Solver.add(CPS.InSetConstraint(domain), [self.LHS])
        
    def __call__(self, Assignment):
        return self.op(Assignment[self.LHS], self.RHS)

    def __repr__(self):
        return str(self.LHS) + self.op_str + str(self.RHS)

class KFormulaRelNode(object):
    def __init__(self, toks):
        self.LHS = toks[0]
        self.op_str = toks[1]
        self.op = OperatorEval[toks[1]]
        self.RHS = toks[2]
            
    def initialize(self, Model):
        self.LHS = self.LHS.initialize(Model)
        self.RHS = self.RHS.initialize(Model)

    def toSQL(self):
        return str(self.LHS)+self.op_str+str(self.RHS)

    def used_variables(self):
        return set([self.LHS, self.RHS])

    def addConstraints(self, Solver):
        if self.op_str=='!=':
            Solver.add(CPS.AllDifferentConstraint(), [self.LHS, self.RHS])
        elif self.op_str=='=':
            Solver.add(CPS.AllEqualConstraint(), [self.LHS, self.RHS])
        else:
            parameters = [self.LHS, self.RHS]
            Solver.add(CPS.FunctionConstraint(FuncWrapper(self.op, parameters)), parameters)

    def __call__(self, Assignment):
        return self.op(Assignment[self.LHS], Assignment[self.RHS])

    def __repr__(self):
        return str(self.LHS) + self.op_str + str(self.RHS)




Component = PYP.Word(PYP.alphas, PYP.alphanums, 1)
Component.setParseAction(ComponentNode)

Operand = Activity | Component
ParametersAtom = Operand + Operator + Operand
ParametersAtom = (Component + Operator + Activity) | (Component + Operator + Component)
ParametersAtom.setParseAction(ParametersAtomNode)

ParametersFormula = PYP.operatorPrecedence(ParametersAtom, [(Not, 1, PYP.opAssoc.RIGHT, NotNode),
                                                            (And,  2, PYP.opAssoc.LEFT, AndNode),
                                                            (Or, 2, PYP.opAssoc.LEFT, OrNode),
                                                            (Implies, 2, PYP.opAssoc.LEFT, ImpliesNode)])
ParametersFormula.setParseAction(ParametersFormulaNode)

Parameters = ParametersFormula + PYP.Suppress(',') + Component
Parameters.setParseAction(ParametersNode)

K = PYP.Suppress(PYP.Literal('K_')) + Component + PYP.Suppress(PYP.Literal('_')) + PYP.Word(PYP.nums)
K.setParseAction(KNode)
KFormulaAbs = (K + Operator + Activity) | (Activity + Operator + K)
KFormulaAbs.setParseAction(KFormulaAbsNode)
KFormulaRel = K + Operator + K
KFormulaRel.setParseAction(KFormulaRelNode)


