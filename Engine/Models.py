import itertools as IT
import TransitionGraphs


class Component():
    def __init__(self, index, name, Max):
        self.index = index
        self.name = name
        self.max = Max
        self.range = range(Max+1)
        self.targets = []
        self.regulators = []
        self.parameters = []

    def __repr__(self):
        return self.name

    def __hash__(self):
        return self.index

    def __eq__(self, other):
        return self.index == hash(other)

    def __lt__(self, other):
        return self.index < hash(other)
 
class Parameter():
    def __init__(self, index, owner, context, Range):
        self.index = index
        self.owner = owner
        self.context = context
        self.range = Range
        self.name = 'K_'+str(owner)+'_'+''.join([str(min(context[reg])) for reg in sorted(context.keys())])

    def __hash__(self):
        return self.index

    def __eq__(self, other):
        return self.index == hash(other)

    def __lt__(self, other):
        return self.index < hash(other)

    def __repr__(self):
        return self.name

class Interface():
    def __init__(self, Names, Interactions):
        self.interactions = Interactions
        self.components = []
        self.parameters = []

        names = set([name for name,Max in Names])
        if len(names)<len(Names):
            raise Exception('Duplicate component definition in "%s"'%Names)

        
        index = 0
        for name, Max in sorted(Names, key=lambda x:x[0]):
            comp = Component(index, name, Max)
            self.components.append(comp)
            index +=1
        self.components = tuple(self.components)

        pairs = set([(n1,n2) for n1,n2,thrs in Interactions])
        if len(pairs)<len(Interactions):
            raise Exception('Duplicate interactions in "%s"'%Interactions)

        names = set([n[0] for n in Interactions]+[n[1] for n in Interactions])
        diff = names.difference( set([c.name for c in self.components]) )
        if diff:
            diff = ','.join( [str(d) for d in diff] )
            raise Exception( 'Undefined components in interactions: %s. spelling?'%diff )
        
        for name1, name2, thresholds in Interactions:
            
            for comp in self.components:
                if comp.name==name1:
                    comp1 = comp
                if comp.name==name2:
                    comp2 = comp

            if len(set(thresholds))<len(thresholds):
                raise Exception('Duplicate thresholds in "%s,%s,%s"'%(name1,name2,thresholds))

            if set(thresholds).difference(set(range(comp1.max+1))):
                raise Exception('Thresholds "%s,%s,%s" outside activities "0..%i" of "%s".'%(name1,name2,thresholds,comp1.max,comp1))
            
            comp1.targets.append((comp2, thresholds))
            comp2.regulators.append((comp1, thresholds))


        for comp in self.components:
            comp.targets = tuple(sorted(comp.targets))
            comp.regulators = tuple(sorted(comp.regulators))

        
        index = 0 
        for comp in self.components:

            combinations = []
            for reg,thrs in comp.regulators:
                local = []
                thrs = list(thrs)
                thrs.append(reg.max+1)
                lhs = 0
                for rhs in thrs:
                    local.append((reg, tuple(range(lhs,rhs))))
                    lhs = rhs
                combinations.append(local)

            for combination in IT.product(*combinations):
                context = dict(combination)
                
                if context.has_key(comp):
                    act = context[comp]
                    lhs = max(0,min(act)-1)
                    rhs = min(comp.max, max(act)+1)
                    Range = tuple(range(lhs,rhs+1))
                else:
                    Range = tuple(range(comp.max+1))
                #Range = tuple(range(comp.max+1)) # NAIV ENUMERATION

                p = Parameter(index, comp, context, Range)
                comp.parameters.append(p)
                self.parameters.append(p)
                index +=1

            comp.parameters = tuple(sorted(comp.parameters))

        self.parameters = tuple(sorted(self.parameters))

    def sync_successor(self, Params, State):
        return TransitionGraphs.sync_successor(self.components, Params, State)

    def async_successors(self, Params, State):
        return TransitionGraphs.async_successors(self.components, Params, State)

    def async_attractors(self, Params, IniStates):
        return TransitionGraphs.async_attractors(self.components, Params, IniStates)

    def get_equations(self, Params):
        pass
        
    def info(self, verbose=0):
        print 'Network information:'
        i=1
        for comp in self.components:
            print '  ',comp.name.ljust(8),'(max=%i)'%comp.max,'targets:',', '.join(['%s(t=%s)'%(name,','.join([str(t) for t in thrs])) for name,thrs in comp.targets])
            for p in comp.parameters:
                if verbose>0:
                    print '  ',str(p).ljust(8),'(range=%i..%i)'%(min(p.range),max(p.range))
                i*=len(p.range)
        print 'Parameters per component:',','.join([str(comp)+':'+str(len(comp.parameters)) for comp in self.components])
        print 'Possible parametrizations:',i



def PrintFullInfo(Model):
    print "Components:"
    for comp in Model.components:
        print comp.name,'(index=%i,max=%i)'%(comp.index,comp.max),'targets:',', '.join(['%s thrs=%s'%(name,thrs) for name,thrs in comp.targets])
    print "Parameters:"
    i=1
    for p in Model.parameters:
        print "\t",p.index,"=",p, p.context, 'range=',p.range
        i*=len(p.range)
    print "%i feasible parametrizations."%i



    

    
