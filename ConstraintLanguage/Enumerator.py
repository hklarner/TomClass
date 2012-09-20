
import itertools as IT
import constraint as CP
import operator as OP

import ConstraintExpression
reload(ConstraintExpression)

def CreateDataBase(Model, FormulaString):
    pass

def ArgsToDict(Function, Variables):
    def closure(*args):
        Assignment = dict(zip(Variables, args))
        return Function(Assignment)
    return closure

def Parametrizations(Model, FormulaString):
    print 'Constraints formula:',
    if len(FormulaString)>30:
        print '"'+FormulaString[:30]+'.."'
    else:
        print '"'+FormulaString+'"'
    print 'Parsing...',
    Constraint = ConstraintExpression.Formula.parseString(FormulaString, parseAll=True)[0]
    print 'ok'
    
    print 'Initializing Model...',
    Constraint.initialize(Model)
    print 'ok'

    parameters = set(Model.parameters)
    used_params = Constraint.used_variables()
    free_params = sorted(parameters.difference(used_params))
    
    print 'Setting up constraint problem.'
    print 'Free variables:', len(free_params), '/', len(parameters)
    print 'Feasible parametrizations:',reduce(OP.mul,[len(p.range) for p in parameters])
    prob= CP.Problem()
    for p in parameters:
        prob.addVariable(p, p.range)

    count = []
    for sub_constraint in Constraint:
        variables = sorted(sub_constraint.used_variables())
        count.append(str(len(variables)))
        prob.addConstraint(CP.FunctionConstraint(ArgsToDict(sub_constraint, variables)), variables)
    print 'Added',len(count),'constraints on',','.join(count),'variables.'
    
    print 'Enumerating..',
    MAX = 100000
    i = 0

    if free_params:
        Ranges = [p.range for p in free_params]
        for sol in prob.getSolutionIter():
            for free in IT.product(*Ranges):
                sol.update(dict(zip(free_params, free)))
                i+=1
                yield sol
                if i>=MAX: break
            if i>=MAX: break
    else:
        
        for sol in prob.getSolutionIter():
            i+=1
            yield sol
            if i>=MAX: break
    

    print 'got',i,'solutions.',
    if i>=MAX: print 'Reached MAX =',MAX
    else: print

        
