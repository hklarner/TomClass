

import networkx as nx

def Primes_to_SMV( Primes, Fname, InfluenceReduction, UseTrans, Verbose):

    if 0: #RemoveConstants: # (depreceated)
        remove = []
        for k in Primes:
            for v in Primes[k]:
                if Primes[k][v]==[{}]: # constant
                    if not k in remove:
                        remove.append( k )
        for k in remove:
            Primes.pop( k )

    if InfluenceReduction: # remove components that do not influence this list
        ig = nx.DiGraph()
        for n in Primes:
            for v in Primes[n]:
                for prime in Primes[n][v]:
                    ig.add_edges_from([(regulator,n) for regulator in prime])

        candidates = set(Primes.keys())

        if not set(InfluenceReduction).issubset(candidates): # safety
            print '  ooops. incompatible influence reduction. spelling?',
            print ','.join([c for c in InfluenceReduction if not c in candidates ])
            raise Exception

        Components=set([])
        for comp in candidates:
            hit = False
            for target in InfluenceReduction:
                if nx.has_path( ig, comp, target ):
                    hit = True
                    Components.add( comp )
                    break
    else:
        Components=Primes.keys()

    if Verbose>1:
        print '  SMV export: %i/%i components.'%(len(Components),len(Primes))
    if Verbose>2:
        print '  removed:',','.join([name for name in Primes if not name in Components])
        
    
    s  = 'MODULE main\n'
    s += 'DEFINE\n'
    for comp in Components:
        s +='\t%simage := \n\t\tcase\n'%comp
        hit = False
        for v in Primes[comp]:
            for d in Primes[comp][v]:
                const = v
                if d:
                    hit=True
                    condition = ' & '.join([ '%s=%i'%item for item in d.items() ])
                    s += '\t\t\t%s: %i;\n'%(condition,v)

        if hit:
            s += '\t\t\tTRUE: 0;\n'
        else:
            s += '\t\t\tTRUE: %i;\n'%const
        s += '\t\tesac;\n'
        s += '\t%sdif := %simage - %s;\n'%(comp,comp,comp)
        s += '\tdelta%s := %sdif >0?1:%sdif<0?-1:0;\n\n'%(comp,comp,comp)

    condition = ', '.join(['(delta%s!=0)'%comp for comp in Components])
    s += '\tDelta := count(%s);\n\n'%condition

    s += 'VAR\n'
    for comp in Components:
        s += '\t%s: 0..%i;\n'%(comp,max(Primes[comp]))

    s += '\nASSIGN\n'
    
    if UseTrans:
        for comp in Components:
            s += '\tnext(%s) :={%s, %s+delta%s};\n'%(comp,comp,comp,comp)

        condition = ','.join(['(next(%s)!=%s)'%(n,n) for n in Components])
        s += '\nTRANS Delta=0 | count(%s)=1;\n'%condition

    else:
        order = sorted(Components)
        for i,comp in enumerate(order):
            previous = []
            if i>0:
                previous = order[:i]
            after = []
            if i<len(order):
                after = order[i+1:]
            
            s += '\tnext(%s) :=\n'%comp
            s += '\t\tcase\n'
            s += '\t\t\tdelta%s=0: %s;\n'%(comp,comp)
            if previous:
                s += '\t\t\t'+'|'.join(['next(%s)!=%s'%(p,p) for p in previous])+': %s;\n'%comp
            if after:
                s += '\t\t\t'+'|'.join(['delta%s!=0'%a for a in after])+': {%s, %s+delta%s};\n'%(comp,comp,comp)
            s += '\t\t\tTRUE: %s+delta%s;\n'%(comp,comp)
            s += '\t\tesac;\n'

    s += '\n\n\n'

    f = open( Fname, 'w' )
    f.write( s )
    f.close()
    print 'Created', Fname
    
