

#import gurobipy
import itertools as IT
import sys
import networkx as nx
import datetime

def remove( Primes, Components ):
    new_primes = {}
    for name in Primes:
        if name in Components:
            Components.pop(Components.index(name))
            continue

        new_primes[name] = {}
        for value in Primes[name]:
            new_primes[name][value]=[]
            for p in Primes[name][value]:
                new_primes[name][value].append( dict(p.items()) )

    if Components:
        print 'Check spelling, could not remove',','.join(Components)

    return new_primes


def compute_inputs( Primes ):
    res = {}
    for name in Primes:
        hit=True
        for value in Primes[name]:
            if Primes[name][value]!=[{name:value}]:
                hit=False

        if hit: res[name]=Primes[name].values()

    return res


def compute_constants( Primes ):
    res = {}
    for name in Primes:
        for value in Primes[name]:
            if Primes[name][value]==[{}]: # const.
                res[name]=value

    return res


def compute_bifurcationtree( Primes, Region, Verbose ):

    # main loop
    scenarios = [(Primes, Region)]
    depth = 0
    while scenarios:

        depth+=1
        primes, region = scenarios.pop()
        circuits = compute_circuits( primes, Verbose)


        # Divide circuits into consistent sets
        branching_sets = []
        while circuits:

            x = circuits.pop()
            hit=False
            for Class in branching_sets:
                consistent=True
                for y in Class:
                    critical = set(x.items()).intersection(set(y.items()))
                    if critical:
                        if False:
                            print ' **oops: x and y are circuits that contain each other with non-equal scope.'
                            print '      x:',','.join(['%s=%i'%item for item in x.items()])
                            print '      y:',','.join(['%s=%i'%item for item in branching_sets[y][0].items()])
                            raise Exception
                        consistent = False
                        branching_sets.append( x )
                        break


            if not hit: branching_sets[tuple(sorted(x))]=[x]

        print '  Depth=%i. Found'%depth,len(branching_mSRs),'branching points.'
        print "branching_mSRs"
        for k in branching_mSRs:
            print branching_mSRs[k]

        # Pick a combination from branching sets
        constants = compute_constants( primes, region )
        if branching_mSRs:

            space = [range(len(branching_mSRs[x])) for x in branching_mSRs]
            for indicator in IT.product(space):

                newconstants = {}
                for i, k in enumerate(branching_mSRs):

                    newconstants.update( branching_mSRs[k][indicator[i]] )
                c = dict(constants.items() + newconstants.items())

                print '  branching at',','.join(['%s=%i'%item for item in newconstants.items()])
                newprimes, newregion = compute_percolation( primes, c )
                print '     found',','.join(['%s=%i'%item for item in newregion.items()])
                scenarios.append( (newprimes, newregion) )



def compute_percolation( Primes, Constants, Verbose ):
    # returns newprimes, constants
    # newprimes is free of constants.

    if Verbose>0:
        print '   Summary Percolation'
        print '    Components before:',len(Primes)
        print '    Fixed:            ',len(Constants)

    # safety
##    if not set(Constants).issubset(set(Primes.keys())):
##            print '  ooops, incompatible set of constants. spelling?',
##            print ','.join([c for c in Constants if not c in Primes ])
##            raise Exception

    # copy primes
    newconstants = dict(Constants.items())
    newprimes = {}
    for name in Primes:
        if name in Constants: continue
        newprimes[name] = {}
        for value in Primes[name]:
            newprimes[name][value]=[]
            for p in Primes[name][value]:
                newprimes[name][value].append(dict(p))

    def Hit(_primes,_constants):
        for n in _primes:
            for k in _primes[n]:
                for p in _primes[n][k]:
                    for name in p:
                        if name in _constants:
                            return n,k,p,name


    # main loop
    hit=True
    while hit:
        hit = Hit(newprimes, newconstants)

        if hit: # constant name appears in prime p of n at k
            n,k,p,name = hit

            if p[name]!=newconstants[name]: # prime is invalid
                newprimes[n][k].remove( p )

            else:
                np = dict([x for x in p.items() if x[0]!=name])

                if np in newprimes[n][k]: # np is already a prime: remove
                    newprimes[n][k].remove( p )

                else:
                    p.pop(name)  # substitute constant: remove n from p
                    if not p: # n is a new constant
                        newprimes.pop(n)
                        assert(n not in newconstants)
                        newconstants[n]=k


    if Verbose>0:
        print '    Percolated:       ',len(newconstants)-len(Constants)
        if Verbose>1:
            print '    New Constants:    ',','.join(['%s=%i'%item for item in newconstants.items() if not item[0] in Constants])
        print '    New network:      ',len(newprimes)


    return newprimes, newconstants



def CircuitId( circuit ):
    Id = sorted(circuit.items())
    return tuple(Id)

def PrimeId( name, value, prime ):
    Id = [name, value] + sorted(prime.items())
    return tuple(Id)


def compute_fixpoints( Primes, Objective, Report, Verbose ):

    assert( Objective in ['max','min', 'all'] )

    if Verbose>0:
        print
        print '   Model has %i components'%len(Primes)
        print '     Boolean: %i'%len([1 for n in Primes if len(Primes[n])==2])
        x = len([1 for n in Primes if len(Primes[n])==3])
        if x: print '     Ternary: %i'%x
        x = len([1 for n in Primes if len(Primes[n])>3])
        if x: print '     Higher : %i'%x
        print '   PIgraph has'
        print '     %i nodes'%len([1 for n in Primes for a in Primes[n] ])
        print '     %i arcs'%len([1 for n in Primes for a in Primes[n] for h in Primes[n][a]])
        print '   Objective:', Objective

    start_time = datetime.datetime.utcnow()
    m = gurobipy.Model()
    m.setParam( 'OutputFlag', False )

    # create arc and meta variables
    arc_variables    = {}
    meta_variables   = {}
    names       = {}
    for name in Primes:
        for value in Primes[name]:
            ID = '%s=%i'%(name,value)
            meta_variables[ID] = m.addVar(lb=0., ub=1., obj=1., vtype=gurobipy.GRB.BINARY, name=ID)
            for i,p in enumerate(Primes[name][value]):
                pid = PrimeId( name, value, p )
                names[pid] = '%s=%i_%i'%(name,value,i)
                arc_variables[pid] = m.addVar(lb=0., ub=1., obj=1., vtype=gurobipy.GRB.BINARY, name=names[pid])

    m.update()


    # safety
    arcs  = [1 for n in Primes for a in Primes[n] for h in Primes[n][a]]
    atoms = [1 for n in Primes for a in Primes[n]]
    assert( len(arc_variables)==len(arcs)   )
    assert( len(meta_variables)==len(atoms) )



    # add consistency constraints
    counter=0
    for name in Primes:
        for value in Primes[name]:
            ID = '%s=%i'%(name,value)
            exp  = gurobipy.quicksum([ arc_variables[PrimeId( name,value,p )] for p in Primes[name][value] ])
            Var = meta_variables[ID]
            m.addConstr( lhs=Var, sense=gurobipy.GRB.LESS_EQUAL, rhs=exp, name=ID+'_consistency_0')
            counter+=1
            for i,p in enumerate(Primes[name][value]):
                exp = arc_variables[PrimeId(name,value,p)]
                m.addConstr( lhs=Var, sense=gurobipy.GRB.GREATER_EQUAL, rhs=exp, name=ID+'_consistency_%i'%i)
                counter+=1

        exp  = gurobipy.quicksum([meta_variables['%s=%i'%(name,value)] for value in Primes[name] ])
        m.addConstr( lhs=exp, sense=gurobipy.GRB.LESS_EQUAL, rhs=1., name=name+'_consistency')
        counter +=1

    m.update()
    if Verbose>0:
        print '     %i component-consistency constraints'%counter



    # add stability constraints
    counter=0
    for name in Primes:
        for value in Primes[name]:
            for p in Primes[name][value]:
                for n2, v2 in p.items():
                    if (n2,v2)==(name,value): continue # no constraints for self-loops
                    #exp  = gurobipy.quicksum([ arc_variables[PrimeId( n2,v2,p2 )] for p2 in Primes[n2][v2] ])
                    exp_meta = meta_variables['%s=%i'%(n2,v2)]
                    exp_arc  = arc_variables[PrimeId(name,value,p)]
                    m.addConstr( lhs=exp_arc, sense=gurobipy.GRB.LESS_EQUAL, rhs=exp_meta, name=names[pid]+'_stability')
                    counter+=1


    if Verbose>0:
        print '     %i stability constraints'%counter




    # set objective
    exp = gurobipy.quicksum( [ v for v in meta_variables.values()] )
    #exp = gurobipy.quicksum( [ v for v in arc_variables.values()] )
    if Objective=='min':
        m.addConstr( exp, gurobipy.GRB.GREATER_EQUAL, 1 )
        m.setObjective( exp, gurobipy.GRB.MINIMIZE )
    elif Objective=='max':
        m.setObjective( exp, gurobipy.GRB.MAXIMIZE )
    else: # Objective='all'
        exp = gurobipy.quicksum([])
        m.setObjective( exp, gurobipy.GRB.MAXIMIZE )
    m.update()


    # solution loop
    m.optimize()
    finished = (m.status==3)

    counter=0
    ARC_PIDS  = set([])
    FIXPOINTS = set([])

##    # auxillary functions for constructing constraints
##    def get_opposites(IDS):
##        current = dict([ID.split('=') for ID in IDS])
##        targets = []
##        for pid in meta_variables:
##            name,value=pid.split('=')
##            if name in current:
##                if value!=current[name]: targets.append( pid )
##        return targets
##
##    def get_others(IDS):
##        names = set([ID.split('=')[0] for ID in IDS])
##        targets = []
##        for pid in meta_variables:
##            name=pid.split('=')[0]
##            if name not in names: targets.append( pid )
##        return targets


    while not finished:

        # safety
        for pid, x in meta_variables.items()+ arc_variables.items():
            if x.x:
                if not x.x==1:
                    print '  **oops, non-binary solution value:',x,x.x
                    raise Exception

        # extract arc-ids
        pids     = []
        for pid, x in arc_variables.items():
            if x.x: pids.append( pid )
        if pids:
            ARC_PIDS.add( tuple(sorted(pids)) )

        # add new-solutions constraint
        solution  = [pid for pid, x in meta_variables.items() if x.x==1]
        fpoint = tuple(sorted( solution ))

        if fpoint in FIXPOINTS:
            print '  **previous solutions:\n',FIXPOINTS
            print '  **oops, duplicate solution:', ','.join(fpoint)
            print '  **total:',len(FIXPOINTS)
            raise Exception

        if fpoint:
            FIXPOINTS.add( fpoint )

        if Objective=='min':
            exp = gurobipy.quicksum( [meta_variables[pid] for pid in solution] )
            m.addConstr( exp, gurobipy.GRB.LESS_EQUAL, len(solution)-1 )

        elif Objective=='max':
            exp = gurobipy.quicksum( [meta_variables[pid] for pid in meta_variables if not pid in solution] )
            m.addConstr( exp, gurobipy.GRB.GREATER_EQUAL, 1 )

        else:
            exp1 = gurobipy.quicksum( [meta_variables[pid] for pid in solution] )
            exp2 = gurobipy.quicksum( [1-meta_variables[pid] for pid in meta_variables if not pid in solution] )
            m.addConstr( exp1+exp2, gurobipy.GRB.LESS_EQUAL, len(meta_variables)-1 )


        m.update()
        m.optimize()
        finished = m.status==3
        counter+=1
        if counter%10000==0:
            print '  ** reached iteration limit %i: stopped'%counter
            finished = True

    end_time = datetime.datetime.utcnow()
    duration = end_time - start_time

    # extract
    # - ARCSETS: the stable arc set in double-dict form
    ARCSETS = []
    #FIXPOINTS = []
    for pids in ARC_PIDS:
        arcs   = {}
        pstate = {}
        for pid in pids:
            name         = pid[0]
            value        = pid[1]
            if name in pstate:
                # safety
                if value != pstate[name]:
                    print '  **oops: inconsistency: %s=%i and %i'%(name,pstate[name],value)
                    raise Exception
            pstate[name] = value

            arcs[name] = {}
            arcs[name][value] = dict( [(n,v) for n,v in pid[2:]] )




        # append arcs and pstate
        arc_limit = 1000
        if len(ARCSETS)<arc_limit:
            ARCSETS.append( arcs )
        elif len(ARCSETS)==1000:
            print 'reached limit %i, do not store arc sets anymore..'%arc_limit






    days, seconds = duration.days, duration.seconds
    time_stamp = int(seconds)
    hours = days * 24 + seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    time_delta = '%id %ih %im %is'%(days,hours,minutes,seconds)

    FIXPOINTS = sorted(FIXPOINTS, key=lambda x:len(x), reverse=True)
    sizes = {}
    for fp in FIXPOINTS:
        x = len(fp)
        if not x in sizes: sizes[x]=0
        sizes[x]+=1

    if Verbose>0:
        print '   Solutions Summary:'
        print '     Runtime:     ',time_delta
        print '     Objective:   ',Objective
        print '     Iterations:   %i'%counter
        print '     Fixpoints:   ',len( FIXPOINTS )
        print '      n=%i'%(len(meta_variables)/2)
        print '      Sizes:      ',','.join([str(sizes[x])+'x'+str(x) for x in sorted(sizes, reverse=True)])
        print '     Arc sets:    ',len( ARCSETS )

    if Report:
        max_length = max([len(n) for n in Primes])+2
        s=''
        for i,aset in enumerate(ARCSETS):
            s+= ' --- fixpoint %i --------------\n'%i
            for n in aset:
                for v in aset[n]:
                    s+= '   '+str(n).ljust(max_length)+'='+str(v)+'  '+str( aset[n][v] )+'\n'

        f = open(Report, 'w')
        f.writelines(s)
        f.close()

    result = []
    for fp in FIXPOINTS:
        res={}
        for ID in fp:
            name, value = ID.split('=')
            res[name] = int(value)
        result.append( res )


    return time_stamp, result




def compatible( Fpoint1, Fpoint2 ):
    keys = set(Fpoint1.keys()).intersection(set(Fpoint2.keys()))
    for k in keys:
        if Fpoint1[k]!=Fpoint2[k]: return False
    return True

def compute_cliques( Fixpoints ):
    indeces = range(len(Fixpoints))
    graph = nx.Graph()
    for i1 in indeces:
        fpoint1 = Fixpoints[i1]
        for i2 in indeces:
            fpoint2 = Fixpoints[i2]
            if fpoint1==fpoint2: continue
            if compatible(fpoint1,fpoint2):
                graph.add_edge( i1, i2 )

    cliques = []
    for clique in nx.find_cliques(graph):
        cliques.append( [Fixpoints[i] for i in clique] )
    return cliques


# compute_fixpoints( Primes, Objective, Report, Verbose ): FIXPOINTS
# compute_percolation( Primes, Constants, Verbose ): newprimes, newconstants
# compute_constants( Primes ): constants

def copy_primes( Primes ):
    newprimes = {}
    for name in Primes:
        newprimes[name] = {}
        for value in Primes[name]:
            newprimes[name][value]=[]
            for p in Primes[name][value]:
                newprimes[name][value].append(dict(p))
    return newprimes


def compute_structure( Primes, Report, Verbose, Reasoning ):
    assert( Reasoning in ['brave', 'cautious'] )

    #test = compute_fixpoints( Primes=Primes, Objective='max', Report=False, Verbose=-9)
    #print len(test)

    layers = 1
    cores  = 0

    constants = compute_constants( Primes )
    newprimes, newconstants = compute_percolation( Primes=Primes, Constants=constants, Verbose=-9 )

    STACK  = [(newprimes, newconstants)]
    MAXIMA = []

    DONE = []

    start_time = datetime.datetime.utcnow()
    while STACK:

        initial_primes, initial_constants = STACK.pop()
        minima = compute_fixpoints( Primes=initial_primes, Objective='min', Report=False, Verbose=-9)

        cores += len(minima)

        if not minima:
            if not initial_constants in MAXIMA:
                MAXIMA.append( initial_constants )
            continue

        if Reasoning=='cautious':
            for m in minima:
                constants = dict(initial_constants)
                constants.update( m )

                if constants in DONE:
                    continue
                DONE.append( constants )

                newprimes, newconstants = compute_percolation( Primes=initial_primes, Constants=constants, Verbose=-9 )

                if not newprimes:
                    if not newconstants in MAXIMA:
                        MAXIMA.append( newconstants )
                    continue

                STACK.append( (newprimes, newconstants) )


        else: # Reasoning=='brave'


            if len(minima)>1:
                seeds  = compute_cliques( minima )
            else:
                seeds = [minima]
            print 'length seeds:',len(seeds)

            for seed in seeds:

                layers += 1

                constants = dict(initial_constants)
                for m in seed: constants.update( m )

                newprimes, newconstants = compute_percolation( Primes=initial_primes, Constants=constants, Verbose=-9 )

                if not newprimes:
                    #print 'steady state'
                    MAXIMA.append( newconstants )
                    continue

                STACK.append( (newprimes, newconstants) )



    print 'total:        ',len(MAXIMA)
    print 'steady states:',len([1 for M in MAXIMA if len(M)==len(Primes)])
    print 'other:        ',len([1 for M in MAXIMA if len(M)!=len(Primes)])

    end_time = datetime.datetime.utcnow()
    duration = end_time - start_time
    days, seconds = duration.days, duration.seconds
    hours = days * 24 + seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    time_delta = '%id %ih %im %is'%(days,hours,minutes,seconds)
    print 'Runtime:      ',time_delta
