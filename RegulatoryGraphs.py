import itertools as IT


class Component():
    def __init__(self, index, name, Max):
        self.name = name
        self.index = index
        self.max = Max
        self.targets = []
        self.regulators = []
        self.thresholds_to = {}
        self.thresholds_from = {}
        self.contexts = []
        self.context_by_intensity = {}       

    def __repr__(self):
        return self.name

    def __hash__(self):
        return self.index

    def __eq__(self, other):
        return self.index == hash(other)

    def __ne__(self, other):
        return self.index != hash(other)

    def __lt__(self, other):
        return self.index < hash(other)

    def __le__(self, other):
        return self.index <= hash(other)

    def __gt__(self, other):
        return self.index > hash(other)

    def __ge__(self, other):
        return self.index >= hash(other)

    def activity_slice(self, operator, bound):
        if operator=='=':
            return set([bound])
        elif operator=='>':
            return set(range(bound+1,self.max+1))
        elif operator=='<':
            return set(range(0,bound))
        elif operator=='>=':
            return set(range(bound,self.max+1))
        elif operator=='<=':
            return set(range(0,bound+1))
        elif operator=='!=':
            s = set(range(0,self.max+1))
            s.remove(bound)
            return s
 
class Context():
    def __init__(self, index, owner, intensities, intervals, Range):
        self.index = index
        self.owner = owner
        self.intensities = intensities
        self.intervals = intervals
        self.range = Range

    def __hash__(self):
        return self.index

    def __eq__(self, other):
        return self.index==hash(other)

    def __repr__(self):
        return 'K_%s_%s'%(self.owner,''.join([str(i) for i in self.intensities]))

class Model():
    def __init__(self, Names, Interactions):
        components = []
        component_by_name = {}
        parameters = {}
        
        index = 0
        for name, Max in sorted(Names, key=lambda x:x[0]):
            comp = Component(index, name, Max)
            component_by_name[name] = comp
            components.append(comp)
            
            index +=1
            
        for name1, name2, thresholds in Interactions:
            comp1 = component_by_name[name1]
            comp2 = component_by_name[name2]
            comp1.targets.append((comp2, thresholds))
            comp2.regulators.append((comp1, thresholds))

        
        index_count = 0
        
        for comp in components:
            comp.targets.sort()
            comp.regulators.sort()

            regs = comp.regulators
            
            all_intensities = IT.product(*[range(len(thrs)+1) for source,thrs in regs])

            for intensities in all_intensities:

                intervals = {}
                param_range = range(comp.max+1)
                for i, inten in enumerate(intensities):
                    source, thrs = regs[i]
                    
                    if inten:
                        if inten==len(thrs):
                            s = set(range(thrs[inten-1],source.max+1))
                            cut = range(thrs[inten-1]-1,source.max+1)
                        else:
                            s = set(range(thrs[inten-1],thrs[inten]))
                            cut = range(thrs[inten-1]-1,thrs[inten]+1)
                    else:
                        s = set(range(thrs[0]))
                        cut = range(thrs[0]+1)

                    if source == comp:
                        param_range=cut
                        
                    intervals[source] = s
                
                con = Context(index_count, comp, intensities, intervals, param_range)
                parameters[con] = con
                comp.contexts.append(con)
                comp.context_by_intensity[intensities] = con
                index_count +=1

        self.components = components
        self.component_by_name = component_by_name
        self.parameters = parameters

def MS_simple():
    Names = [('m1', 1),('m2', 1),('rr', 1),('bb', 1),('gg',1)]
    Interactions = [('m1','m1',(1,)),
                    ('m2','m2',(1,)),
                    ('m2','rr',(1,)),
                    ('m1','rr',(1,)),
                    ('bb','rr',(1,)),
                    ('gg','rr',(1,)),]
    return Model(Names, Interactions)

def MS():
    Names = [('M', 2),('rr', 1),('bb', 1),('gg', 1)]
    Interactions = [('M','M',(1,2)),
                    ('M','rr',(1,2)),
                    ('bb','rr',(1,)),
                    ('bb','gg',(1,)),
                    ('bb','bb',(1,)),
                    ('gg','gg',(1,)),
                    ('gg','bb',(1,)),
                    ('gg','rr',(1,)),
                    ('rr','gg',(1,)),
                    ('rr','bb',(1,)),
                    ('rr','rr',(1,))]
    return Model(Names, Interactions)

def RunningExample():
    Names = [('v1',2),('v2',2)]
    Interactions = [('v1','v1',(1,)),
                    ('v1','v2',(1,2)),
                    ('v2','v1',(1,)),
                    ('v2','v2',(2,))]

    return Model(Names, Interactions)

def Toy0():
    Names = [('x',1),('y',1),('z',1),('T',1)]
    Interactions = [('x','T',(1,)),
                    ('y','T',(1,)),
                    ('z','T',(1,))]

    return Model(Names, Interactions)

def Toy1():
    Names = [('w',1),('x',1),('y',1),('z',1),('T',1)]
    Interactions = [('w','T',(1,)),
                    ('x','T',(1,)),
                    ('y','T',(1,)),
                    ('z','T',(1,))]

    return Model(Names, Interactions)

def Example10():
    Names = [('v0',2),('v1',2),('v2',2),('v3',2),
             ('v4',2),('v5',2),('v6',2),
             ('v7',2),('v8',2),('v9',2)]
    Interactions = [('v0', 'v0', (1, 2)), ('v0', 'v1', (1,)), ('v0', 'v2', (2,)), ('v0', 'v3', (2,)), ('v0', 'v4', (1,)), ('v0', 'v5', (1,)), ('v0', 'v6', (2,)), ('v0', 'v7', (1,)), ('v0', 'v8', (1,)), ('v0', 'v9', (2,)), ('v1', 'v0', (1, 2)), ('v1', 'v1', (1, 2)), ('v1', 'v2', (1,)), ('v1', 'v3', (1,)), ('v1', 'v4', (1,)), ('v1', 'v5', (1, 2)), ('v1', 'v6', (1,)), ('v1', 'v7', (1,)), ('v1', 'v8', (1,)), ('v1', 'v9', (1,)), ('v2', 'v0', (2,)), ('v2', 'v1', (1,)), ('v2', 'v2', (1,)), ('v2', 'v3', (1,)), ('v2', 'v4', (1,)), ('v2', 'v5', (1,)), ('v2', 'v6', (1, 2)), ('v2', 'v7', (2,)), ('v2', 'v8', (1, 2)), ('v2', 'v9', (1,)), ('v3', 'v0', (1, 2)), ('v3', 'v1', (1, 2)), ('v3', 'v2', (2,)), ('v3', 'v3', (1, 2)), ('v3', 'v4', (1, 2)), ('v3', 'v5', (2,)), ('v3', 'v6', (2,)), ('v3', 'v7', (2,)), ('v3', 'v8', (2,)), ('v3', 'v9', (1,)), ('v4', 'v0', (1,)), ('v4', 'v1', (1,)), ('v4', 'v2', (1, 2)), ('v4', 'v3', (2,)), ('v4', 'v4', (2,)), ('v4', 'v5', (2,)), ('v4', 'v6', (1, 2)), ('v4', 'v7', (1, 2)), ('v4', 'v8', (2,)), ('v4', 'v9', (1, 2)), ('v5', 'v0', (1,)), ('v5', 'v1', (2,)), ('v5', 'v2', (1, 2)), ('v5', 'v3', (1, 2)), ('v5', 'v4', (1, 2)), ('v5', 'v5', (1,)), ('v5', 'v6', (1, 2)), ('v5', 'v7', (1,)), ('v5', 'v8', (2,)), ('v5', 'v9', (2,)), ('v6', 'v0', (2,)), ('v6', 'v1', (2,)), ('v6', 'v2', (1, 2)), ('v6', 'v3', (1,)), ('v6', 'v4', (1,)), ('v6', 'v5', (1, 2)), ('v6', 'v6', (1,)), ('v6', 'v7', (1, 2)), ('v6', 'v8', (1, 2)), ('v6', 'v9', (1, 2)), ('v7', 'v0', (1,)), ('v7', 'v1', (2,)), ('v7', 'v2', (1,)), ('v7', 'v3', (2,)), ('v7', 'v4', (1, 2)), ('v7', 'v5', (2,)), ('v7', 'v6', (2,)), ('v7', 'v7', (1, 2)), ('v7', 'v8', (1,)), ('v7', 'v9', (1,)), ('v8', 'v0', (2,)), ('v8', 'v1', (2,)), ('v8', 'v2', (1,)), ('v8', 'v3', (1, 2)), ('v8', 'v4', (2,)), ('v8', 'v5', (1, 2)), ('v8', 'v6', (2,)), ('v8', 'v7', (2,)), ('v8', 'v8', (1, 2)), ('v8', 'v9', (1, 2)), ('v9', 'v0', (1, 2)), ('v9', 'v1', (1, 2)), ('v9', 'v2', (1, 2)), ('v9', 'v3', (1,)), ('v9', 'v4', (2,)), ('v9', 'v5', (1, 2)), ('v9', 'v6', (1,)), ('v9', 'v7', (2,)), ('v9', 'v8', (1, 2)), ('v9', 'v9', (2,))]
    
    return Model(Names, Interactions)
                    
def Example5():
    Names = [('v0',2),('v1',2),('v2',2),('v3',2),('v4',2)]
    Interactions = [('v0', 'v0', (1,)), ('v0', 'v1', (2,)), ('v0', 'v2', (1,)), ('v0', 'v3', (1,)), ('v0', 'v4', (1, 2)), ('v1', 'v0', (1,)), ('v1', 'v1', (2,)), ('v1', 'v2', (1, 2)), ('v1', 'v3', (2,)), ('v1', 'v4', (1, 2)), ('v2', 'v0', (1, 2)), ('v2', 'v1', (1,)), ('v2', 'v2', (2,)), ('v2', 'v3', (1,)), ('v2', 'v4', (1,)), ('v3', 'v0', (1,)), ('v3', 'v1', (2,)), ('v3', 'v2', (2,)), ('v3', 'v3', (2,)), ('v3', 'v4', (1, 2)), ('v4', 'v0', (1, 2)), ('v4', 'v1', (1, 2)), ('v4', 'v2', (1,)), ('v4', 'v3', (1, 2)), ('v4', 'v4', (1,))]
    
    return Model(Names, Interactions)              
            
def Example7():
    Names = [('v0',2),('v1',2),('v2',2),('v3',2),('v4',2),('v5',2),('v6',2)]
    Interactions = [('v0', 'v0', (1, 2)), ('v0', 'v1', (2,)), ('v0', 'v2', (2,)), ('v0', 'v3', (1,)), ('v0', 'v4', (1,)), ('v0', 'v5', (1,)), ('v0', 'v6', (1, 2)), ('v1', 'v0', (2,)), ('v1', 'v1', (1,)), ('v1', 'v2', (2,)), ('v1', 'v3', (1,)), ('v1', 'v4', (1,)), ('v1', 'v5', (2,)), ('v1', 'v6', (2,)), ('v2', 'v0', (1, 2)), ('v2', 'v1', (2,)), ('v2', 'v2', (1, 2)), ('v2', 'v3', (1, 2)), ('v2', 'v4', (1, 2)), ('v2', 'v5', (1, 2)), ('v2', 'v6', (2,)), ('v3', 'v0', (2,)), ('v3', 'v1', (1,)), ('v3', 'v2', (1, 2)), ('v3', 'v3', (1,)), ('v3', 'v4', (1, 2)), ('v3', 'v5', (1,)), ('v3', 'v6', (1, 2)), ('v4', 'v0', (1,)), ('v4', 'v1', (1,)), ('v4', 'v2', (2,)), ('v4', 'v3', (1, 2)), ('v4', 'v4', (1, 2)), ('v4', 'v5', (1, 2)), ('v4', 'v6', (2,)), ('v5', 'v0', (1, 2)), ('v5', 'v1', (1, 2)), ('v5', 'v2', (1, 2)), ('v5', 'v3', (1, 2)), ('v5', 'v4', (2,)), ('v5', 'v5', (1,)), ('v5', 'v6', (2,)), ('v6', 'v0', (2,)), ('v6', 'v1', (1,)), ('v6', 'v2', (2,)), ('v6', 'v3', (1,)), ('v6', 'v4', (1,)), ('v6', 'v5', (1, 2)), ('v6', 'v6', (1, 2))]

    return Model(Names, Interactions)

def Boolean5():
    Names = [('v0',1),('v1',1),('v2',1),('v3',1),('v4',1)]
    Interactions = [('v0', 'v0', (1,)), ('v0', 'v1', (1,)), ('v0', 'v2', (1,)), ('v0', 'v3', (1,)), ('v0', 'v4', (1,)), ('v1', 'v0', (1,)), ('v1', 'v1', (1,)), ('v1', 'v2', (1,)), ('v1', 'v3', (1,)), ('v1', 'v4', (1,)), ('v2', 'v0', (1,)), ('v2', 'v1', (1,)), ('v2', 'v2', (1,)), ('v2', 'v3', (1,)), ('v2', 'v4', (1,)), ('v3', 'v0', (1,)), ('v3', 'v1', (1,)), ('v3', 'v2', (1,)), ('v3', 'v3', (1,)), ('v3', 'v4', (1,)), ('v4', 'v0', (1,)), ('v4', 'v1', (1,)), ('v4', 'v2', (1,)), ('v4', 'v3', (1,)), ('v4', 'v4', (1,))]

    return Model(Names, Interactions)

def Boolean4():
    Names = [('v0',1),('v1',1),('v2',1),('v3',1)]
    Interactions = [('v0', 'v0', (1,)), ('v0', 'v1', (1,)),
                    ('v1', 'v1', (1,)), ('v1', 'v2', (1,)),
                    ('v2', 'v2', (1,)), ('v2', 'v3', (1,)),
                    ('v3', 'v3', (1,)), ('v3', 'v1', (1,)),
                    ('v3', 'v0', (1,))]
    return Model(Names, Interactions)

def Shahrad():
    Names = [('A',1),('B',1),('C',2)]
    Interactions = [('A','C',(1,)),
                    ('B','C',(1,)),
                    ('C','A',(1,)),
                    ('C','B',(1,2)),
                    ('C','C',(1,))]
    return Model(Names, Interactions)


def PrintFullInfo(Model):
    print 'Semantic checks to do:'
    print '\t(1) Interactions agree with components.'
    print '\t(2) Thresholds agree with max activities.'
    print "Components:"
    for comp in Model.components:
        print comp.name,'(index=%i,max=%i)'%(comp.index,comp.max),'targets:',', '.join(['%s thrs=%s'%(name,thrs) for name,thrs in comp.targets])
    print "Parameters:"
    i=1
    for p in Model.parameters:
        print "\t",p.index,"=",p, p.intervals, 'range=%s'%p.range
        i*=len(p.range)
    print "%i feasible parametrizations."%i

    
