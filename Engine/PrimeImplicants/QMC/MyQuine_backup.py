
import qm
import itertools



    


def minimize( Equations, verbose=-1 ):
    if verbose>-1: print 'Minimizing equations..'
    Max = {}
    for name in Equations:
        Max[name] = max(Equations[name])

    minimized   = {}
    for name in sorted(Equations):
        minimized[name] = {}
        for value in Equations[name]:
            Eq = Equations[name][value]
            minimized[name][value] = _solve( Eq, Max, Minimize=True )

            if verbose>1:
                print '%s=%i'%(name,value)
                print '  <',Eq
            if len(minimized[name][value])<len(str(Eq)) and verbose>0:
                print ' >>',minimized[name][value]

    return minimized



def primes( Equations, verbose ):
    if verbose>-1: print 'Computing primes..'
    Max = {}
    for name in Equations:
        Max[name] = max(Equations[name])
        
    primes      = {}
    for name in Equations:
        
        if not name=='STAT5':continue ####
        
        primes[name]    = {}
        for value in sorted(Equations[name], reverse=True):

            if not value==1: continue ####
            print 'value:',value ####
            
            Eq = Equations[name][value]
            primes[name][value] = _solve( Eq, Max, Minimize=False )

            if verbose>0:
                n = '%s=%i:'%(name,value)
                l = ','.join([''.join(['(%s=%i)'%(k,v) for k,v in sorted(p.items())]) for p in primes[name][value]])
                if not l:
                    l='-'
                    if primes[name][value]:
                        l='const.'
                
                print '  ',n.ljust(10), l

            
    return primes



def _solve( Equation, Max, Minimize ):

    # one boolean variable for each threshold
    BooleanVariables = []
    for name in Equation.variables():
        for v in range(Max[name]+1): # for v in range(1,Max[name]+1):
            BooleanVariables.append( '%s=%i'%(name,v) )
    size = len(Equation.variables())

    # sum notation for QM input
    ones = []
    dcs  = []    
    for i,y in enumerate(itertools.product(*len(BooleanVariables)*[[0,1]])):
        y = zip(BooleanVariables,y)
        
        # boolean state to multi value state
        valid = True
        x = {}
        for atom, state in y:
            if state:
                name, value = atom.split('=')
                value = int(value)
            
                if name in x:
                    valid = False
                    break
                x[name] = value

        if not len(x)==size:
            valid=False

        if not valid:
            dcs.append(i)
            pass
        elif Equation(x):
            ones.append(i)

    # run QM
    rev = BooleanVariables[:]
    rev.reverse()
    solver = qm.QM( rev )
    minterms = solver.compute_primes(ones+dcs)

    if Minimize:
        minimized = solver.get_function(  solver.solve( ones,dcs )[1]  )
        minimized = minimized.replace(' AND ',' & ')
        minimized = minimized.replace(' OR ',' | ')
        minimized = minimized.replace('NOT','!')

        return minimized

    # convert minterms to primes
    primes = []
    
    for i,minterm in enumerate(minterms):
        print '---'

        options   = {} #dict([(name,range(Max[name]+1)) for name in Equation.variables()])
        valid = True
        m = []
        for j in xrange(len(rev)):
            name, value = rev[j].split('=')
            value = int(value)
            
            if minterm[0] & 1<<j:# non-negated literal
                #prime[rev[j]]=1
                m.append('%s==%i'%(name,value))
                if options.has_key(name):# invalid prime
                    if not value in options[name]:
                        print 'invalid 1'
                        valid=False
                options[name]=[value]
                
            elif not minterm[1] & 1<<j:# negated literal
                #prime[rev[j]]=0
                m.append('%s!=%i'%(name,value))
                if not options.has_key(name): options[name]=range(Max[name]+1)
                options[name] = [k for k in options[name] if not k==value]
                if not options[name]:
                    valid=False
                    print 'invalid 2'

        print 'minterm:',','.join(sorted(m))
        if not valid: continue

        print 'options:',options.items()
        names  = sorted(options)
        ranges = [options[k] for k in names]

            
        for p in itertools.product( *ranges ):
            p = dict(zip(names,p))
            if p not in primes:
                primes.append( p )
            

    for p in primes:
        print p
        
    return primes
















        
        options   = {} #dict([(name,range(Max[name]+1)) for name in Equation.variables()])
        valid = True
        m = []
        for j in xrange(len(rev)):
            name, value = rev[j].split('=')
            value = int(value)
            
            if minterm[0] & 1<<j:# non-negated literal
                #prime[rev[j]]=1
                m.append('%s==%i'%(name,value))
                if options.has_key(name):# invalid prime
                    if not value in options[name]:
                        valid=False
                options[name]=[value]
                
            elif not minterm[1] & 1<<j:# negated literal
                #prime[rev[j]]=0
                m.append('%s!=%i'%(name,value))
                if not options.has_key(name): options[name]=range(Max[name]+1)
                options[name] = [k for k in options[name] if not k==value]

        print ','.join(sorted(m))
        if not valid: continue
        
        names  = sorted(options)
        ranges = [options[k] for k in names]

        
        if i==5:
            for k in options:
                print k,options[k]
            
        for p in itertools.product( *ranges ):
            p = dict(zip(names,p))
            if p not in primes:
                primes.append( p )
            

    for p in primes:
        print p
        
    return primes

 




