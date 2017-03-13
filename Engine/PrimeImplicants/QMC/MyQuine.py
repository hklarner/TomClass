
import qm
import itertools



    


def minimize( Equations ):
    Max = {}
    for name in Equations:
        Max[name] = max(Equations[name])

    minimized   = {}
    for name in sorted(Equations):
        minimized[name] = {}
        for value in Equations[name]:
            Eq=Equations[name][value]
            names = [name]+sorted(Eq.variables())
            if any([max(Equations[n])>1 for n in names]):
                minimized[name][value] = 'Non-Boolean'
                continue

            # sum notation for QM input
            names = sorted(Eq.variables())
            ones  = []
            size  = len(names)
            
            for i,y in enumerate(itertools.product(*size*[[0,1]])):
                
                y = dict(zip(names,y))
                if Eq(y): ones.append(i)

            # run QM
            rev = names[:]
            rev.reverse()
            solver = qm.QM( rev )
            minterms = solver.compute_primes(ones)
            dcs = []
            f = solver.get_function(  solver.solve( ones,dcs )[1]  )
            f = f.replace(' AND ',' & ')
            f = f.replace(' OR ',' | ')
            f = f.replace('NOT','!')
            if f[0]=='(' and f[-1]==')': f=f[1:-1]
            
            minimized[name][value] = f
            

    return minimized



def primes( Equations, Verbose ):
    if Verbose>-1: print 'Computing primes..'
    Max = {}
    for name in Equations:
        Max[name] = max(Equations[name])
        
    primes      = {}
    size=0
    for name in Equations:
        
        primes[name]    = {}
        for value in sorted(Equations[name], reverse=True):
            
            Eq = Equations[name][value]
            primes[name][value] = primes_equation( Eq, Max )
            size+=len(primes[name][value])

            if Verbose>1:
                n = '%s=%i:'%(name,value)
                l = ','.join([''.join(['(%s=%i)'%(k,v) for k,v in sorted(p.items())]) for p in primes[name][value]])
                if not l:
                    l='-'
                    if primes[name][value]:
                        l='const.'
                
                print '  ',n.ljust(10), l


    if Verbose>0:
        print ' Components:',len(primes)
        print ' Primes:    ',size

            
    return primes


def primes_equation( Equation, Max ):

    def merge( x, y ):
        i=0
        m={}
        for n in x.keys():
            
            if x[n]!=y[n]:
                i+=1
                if i>1: return False
                u = x[n].union(y[n])
                if len(u)!=max(u)-min(u)+1: return False
                m[n]=u
                
            else:
                m[n]=x[n]

        return m
                

    Names  = sorted(Equation.variables())
    ranges = [range(Max[n]+1) for n in Names]
    minterms = []

    # build minterms
    for x in itertools.product( *ranges ):
        y = dict(zip(Names,x))
        if Equation(y):
            minterms.append( dict(zip(Names,[set([k]) for k in x])) )
            

    if not minterms: return []
    

    # generate table
    table=minterms[:]
        
    # recursive merging
    primes   = []
    finished = False
    while not finished:
        
        ntable = []

        hit    = set([])
        for i,m1 in enumerate(table[:-1]):
            for j,m2 in enumerate(table[i+1:]):

                m3 = merge( m1, m2 )
                if m3:
                    hit.add(i)
                    hit.add(i+1+j)
                    
                    if not m3 in ntable:
                        ntable.append( m3 )

        for i,m in enumerate(table):
            if i not in hit:
                if m not in primes:
                    primes.append( m )

        table = ntable

        if not hit:
            finished=True

    # generate subspaces
    Spaces = []
    for prime in primes:
        z = dict(prime)
        for n in prime:
            if len(prime[n])==Max[n]+1:
                z.pop(n)

        names  = sorted(z)
        ranges = [sorted(z[n]) for n in names]
        for z in itertools.product( *ranges ):
            z = dict(zip(names,z))
            if z not in Spaces:
                Spaces.append( z )

    return Spaces
    



 




