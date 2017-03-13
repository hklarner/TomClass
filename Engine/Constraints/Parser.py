import sys
import pyparsing as PYP
import itertools as IT
import NiemeyerSolver as CPS
import random as RND

import Basics
import Transitions
import EdgeLabel
import Multiplex
import Boolean
import Values

Predicate = Boolean.Grammar ^ Transitions.GrammarFixpoint ^ Transitions.GrammarSubgraph ^ Transitions.GrammarPath ^ EdgeLabel.Grammar ^ \
            Multiplex.Grammar ^ Values.InSet ^ Values.AllEq ^ Values.SomeEq ^ Values.Ineq ^ Basics.KFormulaAbs ^ Basics.KFormulaRel
PredicateFormula = PYP.operatorPrecedence(Predicate,[(Basics.Not, 1, PYP.opAssoc.RIGHT, Basics.NotNode),
                                                     (Basics.And,  2, PYP.opAssoc.LEFT, Basics.AndNode),
                                                     (Basics.Or, 2, PYP.opAssoc.LEFT, Basics.OrNode),
                                                     (Basics.Implies, 2, PYP.opAssoc.LEFT, Basics.ImpliesNode)])


def FuncWrapper(Function, Variables):
    def closure(*args):
        Assignment = dict(zip(Variables, args))
        return Function(Assignment)
    return closure

def FreeSolutions(parameters):
    parameters = list(parameters)
    ranges = [p.range for p in parameters]
    for assignment in IT.product(*ranges):
        yield dict(zip(parameters, assignment))

class Solver():
    def __init__(self, Variables):
        self.variables = set(Variables[:])
        self.constraints = []

    def reset(self):
        self.constraints = []

    def add(self, Constraint, Parameters):
        self.constraints.append((Constraint, Parameters))

    def prepare_solutions(self, verbose=-1):

        free_variables = set(list(self.variables))
        groups = []
        nodes = self.constraints[:]
            
        while nodes:
            c1, v1 = nodes.pop()
            free_variables.difference_update(v1)

            hit = []
            for i,group in enumerate(groups):

                for c2, v2 in group:
                    if set(v1).intersection(set(v2)):
                        group.append((c1,v1))
                        hit.append(i)
                        break

            newgroup = [(c1,v1)]
            for i in hit:
                newgroup.extend(groups[i])
            groups = [g for i,g in enumerate(groups) if i not in hit]
            groups.append(newgroup)

        bound_variables = set([])
        problems = []        
        for group in groups:
            
            problem = CPS.Problem()
            test = CPS.Problem()
            variables = set([])
            
            for c,v in group:
                problem.addConstraint(c,v)
                test.addConstraint(c,v)
                variables.update(set(v))

            if verbose and variables:
                for v in variables: bound_variables.add( v.name )

            for v in variables:
                problem.addVariable(v,v.range)
                test.addVariable(v,v.range)

            if not test.getSolution():
                print '!!No solutions to constraints involving the parameters:'
                print '  '+','.join([str(v) for v in variables])
            problems.append(problem.getSolutionIter())

        if free_variables:
            if verbose>-1:
                print
                print 'Split into',len(groups),'problems.'
                print '  bound variables: ',','.join([str(n) for n in bound_variables])
                print '  free variables:  ',','.join([str(i) for i in free_variables])

            for variable in free_variables:
                problems.append(FreeSolutions([variable]))

            #problems.append(FreeSolutions(free_variables))

        self.problems = problems

    def samples(self, Max, limit = 3000, verbose=-1):
        self.prepare_solutions( verbose )

        local_solutions = []
        for problem in self.problems:
            count = 0
            solutions = []
            for sol in problem:
                solutions.append(sol)
                count+=1
                if count>limit:
                    if verbose>-1: print 'Solutions to local problem larger than "%i". Please increase limit.'%limit
                    return
            local_solutions.append((count,solutions))
        if verbose>-1: print 'Sampling from',len(self.problems),'sets of sizes:',','.join([str(c) for c,s in local_solutions])

        for i in range(Max):
            dicts = []
            for count, sols in local_solutions:
                index = RND.randint(0,count-1)
                for item in sols[index].items():
                    dicts.append(item)
                    
            yield dict(dicts)
        

    def solutions(self, verbose=-1):
        self.prepare_solutions( verbose )

        for dicts in IT.product(*self.problems):
            yield dict([i for d in dicts for i in d.items()])
        

class Interface():
    def __init__(self, Model):
        self.model = Model
        self.solver = Solver( Model.parameters )

    def parse(self, Formula):
        self.solver.reset()
        self.parse_result = []
        if not Formula:
            return
            
        try:
            self.parse_result = PredicateFormula.parseString(Formula, parseAll=True)[0]
            self.parse_result.initialize(self.model)
            
        except PYP.ParseException, err:
            print
            print '-----Parse-Error-------------------------------------'
            print err.line
            print " "*(err.column-1) + "^"
            print err
            print '-----------------------------------------------------'
            raise Exception('stopped')

        

    def info(self):
        print self.parse_result

    def toSQL(self):
        return self.parse_result.toSQL()

    def samples(self, Max, Limit=3000, Verbose=-1):
        if self.parse_result:
            self.parse_result.addConstraints(self.solver)
        return self.solver.samples(Max, Limit, Verbose)

    def solutions(self, verbose=-1):
        if self.parse_result:
            self.parse_result.addConstraints(self.solver)
        return self.solver.solutions(verbose)

def InitialStates(Model, Formula):

    if not Formula:
        return list(IT.product(  *[comp.range for comp in Model.components]  ))
    
    try:
        parse_result = Basics.ParametersFormula.parseString(Formula, parseAll=True)[0]
    except PYP.ParseException, err:
        print
        print '-----Parse-Error-------------------------------------'
        print err.line
        print " "*(err.column-1) + "^"
        print err
        print '-----------------------------------------------------'
        raise Exception('stopped')

    parse_result.initialize(Model)
    solver = Solver(Model.components)
    parse_result.addConstraints(solver)

    states = set([])

    for sol in solver.solutions(verbose=-1):
        states.add(tuple(  [sol[comp] for comp in Model.components]  ))

    return states












        
