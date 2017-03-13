

import gurobipy
import itertools as IT
import sys


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


def compute_branchingtree( Primes, Region, Verbose ):

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


def compute_percolation( Primes, Constants ):
    # returns newprimes, constants
    # newprimes is free of constants.

    s = '   Summary Percolation\n'
    s+= '   Components:   %i\n'%len(Primes)
    
    # copy primes
    constants = dict(Constants.items())
    newprimes = {}
    for name in Primes:
        if name in Constants: continue
        newprimes[name] = {}
        for value in Primes[name]:
            newprimes[name][value]=[]
            for p in Primes[name][value]:
                newprimes[name][value].append(dict(p))

    s+= '   Fixed:        %i\n'%len(Constants)
    s+= '   Free before:  %i\n'%(len(newprimes))

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
        hit = Hit(newprimes, constants)

        if hit: # constant name appears in prime p of n at k
            n,k,p,name = hit

            if p[name]!=constants[name]: # prime is invalid
                newprimes[n][k].remove( p )

            else:
                np = dict([x for x in p.items() if x[0]!=name])
                
                if np in newprimes[n][k]: # np is already a prime: remove
                    newprimes[n][k].remove( p )
                    
                else:
                    p.pop(name)  # substitute constant: remove n from p
                    if not p: # n is a new constant
                        newprimes.pop(n)
                        assert(n not in constants)
                        constants[n]=k

                


    s+= '   Free after:   %i\n'%len(newprimes)
    print s
        
    return newprimes, constants



def CircuitId( circuit ):
    Id = sorted(circuit.items())
    return tuple(Id)

def PrimeId( name, value, prime ):
    Id = [name, value] + sorted(prime.items())
    return tuple(Id)


def compute_fixpoints( Primes, Objective, Verbose ):

    assert( Objective in ['max','min'] )
    
    if Verbose>0:
        print
        print '   Model has %i components'%len(Primes)
        print '     Boolean: %i'%len([1 for n in Primes if len(Primes[n])==2])
        print '     Ternary: %i'%len([1 for n in Primes if len(Primes[n])==3])
        print '     Else   : %i'%len([1 for n in Primes if len(Primes[n])>3])
        print '   PIgraph has'
        print '     %i nodes'%len([1 for n in Primes for a in Primes[n] ])
        print '     %i arcs'%len([1 for n in Primes for a in Primes[n] for h in Primes[n][a]])
        print '   Objective:', Objective
  
    m = gurobipy.Model()
    m.setParam( 'OutputFlag', False )

    # create binary arc-variables
    variables   = {} # arcs
    rowsums     = {} # out-degree of a node
    expressions = {}
    for name in Primes:
        for value in Primes[name]:

            if not (name,value) in expressions:
                expressions[(name,value)] = gurobipy.LinExpr()

            if not (name,value) in rowsums:
                rowsums[(name,value)] = 0
            
            for i,p in enumerate(Primes[name][value]):
                pid = PrimeId( name, value, p )
                #if pid in variables:
                    #print name,value,pid
                    #raise Exception
                variables[pid] = m.addVar(lb=0., ub=1., obj=1., vtype=gurobipy.GRB.BINARY, name='%s=%i_%i'%(name,value,i))

                for item in p.items():
                    if not item in rowsums:
                        rowsums[item] = 0
                    rowsums[item] += 1

    m.update()
            
    # safety
    arcs = [1 for n in Primes for a in Primes[n] for h in Primes[n][a]]
    assert( len(variables)==len(arcs) )


    # add arc-stability constraints
    for name in Primes:
        for value in Primes[name]:
            for p in Primes[name][value]:
                for item in p.items():
                    expressions[item].addTerms( 1., variables[PrimeId( name, value, p )] )
                expressions[(name,value)].addTerms( -1.*rowsums[(name,value)], variables[PrimeId( name, value, p )] )

    for name,value in expressions:
        m.addConstr( expressions[(name, value)], gurobipy.GRB.LESS_EQUAL, 0., '%s=%i'%(name,value) )

    if Verbose>0:
        print '     %i arc-stability constraints'%len(expressions)


        
    # add component-consistency constraints
    counter=0
    for name in Primes:
              
        if 0:
            group = []
            for value in Primes[name]:
                group.extend( [(name,value,p) for p in Primes[name][value]] )
                
            exp = gurobipy.quicksum([ variables[PrimeId( n,v,p )] for n,v,p in group ])
            m.addConstr( exp, gurobipy.GRB.LESS_EQUAL, 1)
            counter+=1
            
        else:
            Sets = []
            for v in Primes[name]:
                if len(Primes[name][v])>0:
                    Sets.append( [(name,v,p) for p in Primes[name][v]] )

            
            for prod in IT.product( *Sets ):
                exp = gurobipy.quicksum([ variables[PrimeId( n,v,p )] for n,v,p in prod])
                m.addConstr( exp, gurobipy.GRB.LESS_EQUAL, 1)
                counter+=1

                  
    m.update()
    if Verbose>0: print '     %i component-consistency constraints'%counter

    # set objective
    exp = gurobipy.quicksum( [ v for v in variables.values()] )
    if Objective=='min':
        m.addConstr( exp, gurobipy.GRB.GREATER_EQUAL, 1 )
        m.setObjective( exp, gurobipy.GRB.MINIMIZE )
    else:
        m.setObjective( exp, gurobipy.GRB.MAXIMIZE )
    m.update()
        

    # solution loop
    m.optimize()
    finished = m.status==3
    PIDS = []

    c=0
    while not finished:
        
        # extract prime-ids
        pids     = []
        for pid, x in variables.items():
            if x.x:
                if not x==1:
                    print '  **oops, non-integer variable:',x,x.x
                    raise Exception
                pids.append( pid )
        PIDS.append( pids )

        # add new-solutions constraint
        if Objective=='min':
            exp = gurobipy.quicksum( [variables[pid] for pid in pids] )
            m.addConstr( exp, gurobipy.GRB.LESS_EQUAL, len(pids)-1 )
            
        else:
            exp = gurobipy.quicksum( [variables[pid] for pid in variables if not pid in pids] )
            #print ' '.join([variables[pid].varname for pid in variables if not pid in pids])
            m.addConstr( exp, gurobipy.GRB.GREATER_EQUAL, 1 )
            
        #print '.',
        #sys.stdout.flush()
        m.update()
        m.optimize()
        finished = m.status==3
        c+=1
        if c%10000==0:
            print '  ** reached iteration %i: stopped'%c
            break
        if finished:
            print '  finished'

    # extract
    # - ARCSETS: the stable arc set in double-dict form
    # - PARTIALSTATES:   the stable partial state in dict form
    ARCSETS = []
    PARTIALSTATES = []
    for pids in PIDS:
        arcs   = {}
        pstate = {}
        for pid in pids:
            name         = pid[0]
            value        = pid[1]
            if name in pstate:
                if value != pstate[name]:
                    print '  **oops: inconsistency: %s=%i and %i'%(name,pstate[name],value)
                    raise Exception
            pstate[name] = value
            
            arcs[name] = {}
            arcs[name][value] = dict( [(n,v) for n,v in pid[2:]] )

            
            
            
        # append arcs and pstate
        if len(ARCSETS)<1000:
            ARCSETS.append( arcs )
        elif len(ARCSETS)==1000:
            print 'do not store arc sets anymore..'



            
        shorter = [p for p in PARTIALSTATES if len(p)<=len(pstate)]
        new = True
        for x in shorter:
            if set(x.items()).issubset(set(pstate.items())):
                new = False
                break
        if new:
            PARTIALSTATES.append( pstate )

            longer  = [p for p in PARTIALSTATES if len(p)>len(pstate)]
            remove = []
            for x in longer:
                if set(pstate.items()).issubset(set(x.items())):
                    remove.append( x )

            for x in remove:
                PARTIALSTATES.remove( x )

        
            

    if Verbose>0:
        print '  found',len( PARTIALSTATES ),'distinct stable partial states.'
        for pstate in PARTIALSTATES:
            print '   -----------------'
            for n,v in sorted(pstate.items()):
                print '  ',n.ljust(10),'=',v
    if Verbose>-1:           
        print '  found',len( PARTIALSTATES ),'distinct stable partial states of lengths:', [len(pstate) for pstate in PARTIALSTATES]
        print '  found',len( ARCSETS ),'distinct stable arc sets.'
        sys.stdout.flush()

    if Verbose>2:
        for aset in ARCSETS:
            print '   -----------------'
            for n in aset:
                for v in aset[n]:
                    print '  ',n.ljust(10),'=',v, aset[n][v]        

    return PARTIALSTATES














        
