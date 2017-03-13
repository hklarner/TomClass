
import itertools as IT


def ConditionalBoolean(Target, Formula, FreeComponents):
    if Formula[0]!='(' or Formula[-1]!=')': Formula = '('+Formula+')'
    
    clauses = []
    for vec in IT.product(*len(FreeComponents)*[['0','1']]):
        cond  = ' and '.join( [c+'='+v for c,v in zip(FreeComponents,vec)]  )
        ones  = 'All('+Formula+' and '+cond+',%s,=,1)'%Target
        zeros = 'All(not '+Formula+' and '+cond+',%s,=,0)'%Target
        clauses.append( '('+ones+' and '+zeros+')'  )

    return '('+' or '.join(clauses)+')'

def AllObservable(Model):
    c = []
    for a,b,ts in Model.interactions:
        for t in ts:
            c.append('Observable(%s,%s,%i)'%(str(a),str(b),t))
    return ' and '.join(c)

def AllMonotonous(Model):
    c = []
    for a,b,ts in Model.interactions:
        for t in ts:
            c.append('(NotInhibiting(%s,%s,%i) or NotActivating(%s,%s,%i))'%(str(a),str(b),t,str(a),str(b),t))
    return ' and '.join(c)

def NegativeCycle(Model, Interactions):
    if not Interactions:
        return ''

    c = []
    for a,b,t in Interactions:
        if not ['hit' for x,y,ts in Model.interactions if a==str(x) and b==str(y) and t in ts]:
            print 'The interaction',a,b,t,'does not exist in the given regulatory graph, please check.'
            raise Exception('The interaction'+str(a)+str(b)+str(t)+'does not exist in the given regulatory graph, please check.')

    if len(Interactions)==1:
        return 'Inhibiting(%s,%s,%i)'%(str(a),str(b),t)

    disjunction = []
    for labels in IT.product(*  [['Inhibiting', 'Activating'] for i in range(len(Interactions)-1)]   ):
        conjunction = []

        sign = 1
        for label, (a,b,t) in zip(labels, Interactions[:-1]):
            if label[0]=='I':
                sign *= -1
            conjunction.append(label+'(%s,%s,%i)'%(str(a),str(b),t))
        if sign==1:
            label = 'Inhibiting'
        else:
            label = 'Activating'
        a,b,t = Interactions[-1]
        conjunction.append(label+'(%s,%s,%i)'%(str(a),str(b),t))

        disjunction.append('('+' and '.join(conjunction)+')')

    return ' or '.join(disjunction)


if __name__=='__main__':
    class toy():
        def __init__(self):
            self.interactions = [('a','b',(1,2)),('b','c',(1,2)),('c','a',(1,))]
    
    print NegativeCycle(toy(), [('a','b',1),('b','c',2),('c','a',1)] )

    print ConditionalBoolean('RAS', 'A=1 and B=1', ['X','Y'])
        
