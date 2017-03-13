
Info = 'Labels by the sorted number of states in each attractor, e.g. "1.1.3.5" '
Info+= 'means there are 4 attractors with 1,1,3 and 5 states in them.'

def Call( STG, States ):
    
    A = STG.attractors( States )

    #label = '.'.join(sorted(  [str(len(a)) for a in A]  ))
    label = str(len(A))
    
    #print '.'.join(str(len(s)) for s in stg.sccs(states))
    #print '----------------'
    

    return label
