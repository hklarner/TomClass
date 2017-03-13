
import Equation
import itertools
import operator
import sys


def read( Lines, CheckSemantics, Verbose ):
    if Verbose>-1: print 'Parsing equations..'
    
    seen    = set([])
    eqs     = {}
    Size    = len(Lines)

    # parse equations
    for i, line in enumerate(Lines):

        line = line.strip()
        if not line: continue
        
        name, eq = line.split(':')
        
        name,value = name.split('=')
        name=name.strip()
        value=int(value)

        eq = eq.strip()
        if not name in eqs:
            eqs[name] = {}
        if value in eqs[name]:
            print ' **error: two equations for',name,'=',value,':'
            print '          ',eq
            print '          ',eqs[name][value]
            raise Exception
        
        if Verbose>1:
            print '\rParsing "%s=%i"                       '%(name,value),
            sys.stdout.flush()
        eqs[name][value] = Equation.parse( eq )

        

    # enforce each variable has an equation
    for name in eqs:
        for val in eqs[name]:
            if val:
                for v in eqs[name][val].variables():
                    if not v in eqs:
                        print ' **error: %s is not defined.'%v
                        print '         ','Appears in "%s"'%str(eqs[name][val])
                        raise Exception
                        

    # enforce one equation for every activity
    Size = len(eqs)
    for j,name in enumerate(eqs):

        # missing equations
        if len(eqs[name])!=max(eqs[name])+1:

            # exactly 1 equation missing
            if len(eqs[name])==max(eqs[name]):
                k = [i for i in range(max(eqs[name])+1) if not i in eqs[name]]
                k = k.pop()

                conjunction = [str(e) for e in eqs[name].values() if str(e)!='0']

                # all e satisfy e=0
                if not conjunction:
                    eq = '1'

                # exists e with e=1
                elif '1' in conjunction:
                    # must be unique!
                    if not len(conjunction)==1:
                        print ' **error: the equations of', name, 'are not disjoint :'
                        print '          ',', '.join(conjunction)
                        raise Exception
                    
                    eq = '0'

                # exists non-trivial e
                else:
                    eq = '&'.join(['!(%s)'%c for c in conjunction])
                    
                eqs[name][k] = Equation.parse( eq )
                if Verbose>1:
                    print '\rParsing "%s=%i"                       '%(name,k),
                    sys.stdout.flush()

            # more than one equation missing
            else:
                print ' **error:',name,' is not well defined:'
                for val in eqs[name]:
                    print '       ',name,'=',val,':',eqs[name][val]
                raise Exception

        
        if len(eqs[name])!=max(eqs[name])+1:
            print ' **error:',name,' is not well defined:'
            for val in eqs[name]:
                print '       ',name,'=',val,':',eqs[name][val]
            raise Exception

        # enforce that exactly one equation is true in every state
        if CheckSemantics:
            dependencies = set([])
            for val in eqs[name]:
                dependencies.update( eqs[name][val].variables() )
            dependencies = sorted(list(dependencies))

            Max = []
            for n in dependencies:
                Max.append( max(eqs[n]) )

            if Verbose>1: print '\rChecking %i/%i. "%s"                '%(j+1,Size,name),
            sys.stdout.flush()
            check( name, eqs[name].values(), dependencies, Max )

    if Verbose>0: print            
    return eqs


def check( Component, Eqs, Names, Max ):
    
    if not Names: return
    if len(Max)>5: return

    hit = set([])
    for a,b in itertools.combinations( Eqs, 2 ):
        
        for values in itertools.product( *[range(m+1) for m in Max] ):
            
            assignment = dict(zip( Names, values ))
            if a(assignment) and b(assignment):
                print ' **error: two equations of', Component, 'are not disjoint :'
                print '         ',a
                print '         ',b
                print '          state:',assignment                
                raise Exception

            if a(assignment) or b(assignment):
                hit.add( values )


    if len(hit)  !=  reduce(operator.mul, [m+1 for m in Max]) :
        print ' **error: equations of',Component,'dont cover all states:'
        for eq in Eqs:
            print '         ',eq
        raise Exception













            
        
    

    
    
    
    
