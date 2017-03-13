import pyparsing as PYP
import operator as OP
import NiemeyerSolver as CPS


import Basics
reload(Basics)


class TransitionsNode(object):
    def __init__(self, s, l, toks):
        self.type = toks[0]
        
        if toks[0]=='Path':
            states = toks[1:]
            transitions = []
            if len(states)>1:
                transitions = zip(states[:-1],states[1:])
            else:
                raise Exception("'%s' must contain at least 2 states, please update."%s)

        if toks[0]=='Fixpoint':
            transitions = [(toks[1],toks[1])]
                
        elif toks[0]=='Subgraph':
            transitions = []
            for tran in toks[1:]:
                src = tran.pop(0)
                for tgt in tran:
                    transitions.append((src,tgt))

        self.transitions = []
        for src,tgt in transitions:
            src = tuple([int(a) for a in src])
            tgt = tuple([int(a) for a in tgt])
            self.transitions.append((src,tgt))

        
    def direction(self, source, target):
        hit = False
        for i, (a1, a2) in enumerate(zip(source, target)):
            
            if a1==a2:
                continue
            elif abs(a1-a2)>1 or hit:
                raise Exception('Transition %s->%s not asynchronous'%(source, target))

            elif a2-a1>0:
                op = OP.gt
                op_str = '>'
            else:
                op = OP.lt
                op_str = '<'
                
            pos = (i, op, op_str)
            hit = True
        return pos

    def initialize(self, Model):
        
        for x in [x for xy in self.transitions for x in xy]:
            if len(x) != len(Model.components):
                raise Exception('State "%s" must be of length %i.'%(x,len(Model.components)))

            for comp, v in zip(Model.components, x):
                if v not in range(comp.max+1):
                                
                    raise Exception('Activity of %s in state %s outside range 0..%s'%(comp, x, comp.max))
                                

        self.requirements = []
        for x, y in self.transitions:
            
            if x==y:
                for comp in Model.components:
                    for p in comp.parameters:
                        if all([x[reg.index] in rng for reg, rng in p.context.items()]):
                            break   
                    self.requirements.append((p, OP.eq, '=', x[comp.index]))

                    
            else:
                i, op, op_str = self.direction(x,y)
                comp = Model.components[i]
                for p in comp.parameters:
                    if all([x[reg.index] in rng for reg, rng in p.context.items()]):
                        break  
                self.requirements.append((p, op, op_str, x[i]))

    def used_variables(self):
        s=set([])
        for p in self.requirements:
            s.add(p[0])
        return s

    def addConstraints(self, Solver):
        for p, op, op_str, val in self.requirements:
            domain = tuple([i for i in p.range if op(i,val)])
            Solver.add(CPS.InSetConstraint(domain), [p])

    def toSQL(self):
        return ' and '.join([str(p)+op_str+str(val) for p, op, op_str, val in self.requirements])
        
    
    def __call__(self, Assignment):
        for con,op,op_str,val in self.requirements:
            if not op(Assignment[con],val):
                return False
        return True

    def __repr__(self):
        return self.type+'('+','.join([str(con)+op_str+str(val) for con,op,op_str,val in self.requirements])+')'




State = PYP.Word(PYP.nums)
GrammarPath = PYP.CaselessLiteral('Path') + PYP.Suppress('(') + PYP.delimitedList(State) + PYP.Suppress(')')
GrammarPath.setParseAction(TransitionsNode)

GrammarFixpoint = PYP.CaselessLiteral('Fixpoint') + PYP.Suppress('(') + State + PYP.Suppress(')')
GrammarFixpoint.setParseAction(TransitionsNode)

Transitions = PYP.Group(State + PYP.Suppress(':') + PYP.Suppress('[') + PYP.delimitedList(State) + PYP.Suppress(']'))
GrammarSubgraph = PYP.CaselessLiteral('Subgraph') + PYP.Suppress('(') + PYP.delimitedList(Transitions) + PYP.Suppress(')')
GrammarSubgraph.setParseAction(TransitionsNode)

    
