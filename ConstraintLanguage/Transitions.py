import pyparsing as PYP
import operator as OP


DeltaOperator = {1:OP.gt, -1:OP.lt}

class TransitionsNode(object):
    def __init__(self, toks):
        self.type = toks[0]
        if toks[0]=='Path':
            states = toks[1:]
            transitions = []
            if len(states)>1:
                for src, tgt in zip(states[:-1],states[1:]):
                    transitions.append((src,tgt))
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
            if a1==a2: continue
            if hit or abs(a1-a2)>1: raise Exception('Transition %s->%s not asynchronous'%(source, target))
            op = DeltaOperator[a2-a1]
            op_str = '>' if a2-a1>0 else '<'
            pos = (i, op, op_str)
            hit = True
        return pos

    def initialize(self, Model):
        components = Model.components
        size = len(components)
        for src, tgt in self.transitions:
            if not len(src)==size and len(tgt)==size:
                raise Exception('States must be of same length')

        for tran in self.transitions:
            for state in tran:
                for comp, act in zip(components, state):
                    if act not in range(comp.max+1):
                        raise Exception('Activity of %s in state %s outside range %s'%(comp, state, comp.range))

        pairs = []
        for source, target in self.transitions:
            if source==target:
                for i,comp in enumerate(components):
                    for con in comp.contexts:
                        for src, tng in con.intervals.items():
                            if all([source[src.index] in rng for src, rng in con.intervals.items()]): break
                    pairs.append((con, OP.eq, '=', source[i]))
            else:
                i, op, op_str = self.direction(source,target)
                comp = components[i]
                for con in comp.contexts:
                    for src, rng in con.intervals.items():
                        if all([source[src.index] in rng for src, rng in con.intervals.items()]): break
                        
                pairs.append((con,op,op_str,source[i]))

        self.pairs = pairs

    def used_variables(self):
        s=set([])
        for p in self.pairs:
            s.add(p[0])
        return s
    
    def __call__(self, Assignment):
        for con,op,op_str,val in self.pairs:
            if not op(Assignment[con],val):
                return False
        return True

    def __repr__(self):
        return self.type+'('+' and '.join([str(con)+op_str+str(val) for con,op,op_str,val in self.pairs])+')'




State = PYP.Word(PYP.nums)
Path = PYP.CaselessLiteral('Path') + PYP.Suppress('(') + PYP.delimitedList(State) + PYP.Suppress(')')
Path.setParseAction(TransitionsNode)

Transitions = PYP.Group(State + PYP.Suppress(':') + PYP.Suppress('[') + PYP.delimitedList(State) + PYP.Suppress(']'))
Subgraph = PYP.CaselessLiteral('Subgraph') + PYP.Suppress('(') + PYP.delimitedList(Transitions) + PYP.Suppress(')')
Subgraph.setParseAction(TransitionsNode)

    
