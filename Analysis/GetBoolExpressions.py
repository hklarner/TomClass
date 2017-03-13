

from Engine import Database
import re #for Logicfun
reload(Database)



def run():

    # specify input:
    name_database='perturbation_example.sqlite'
    ID_model=30
    # all inputs specified
    
    db = Database.Analysis(name_database)
    model = db.readModel()
    partargets = db.export(ID_model)[0]
    db.close()
    #print partargets
    
    print 'Model ',ID_model,' from ',name_database,' represented by logical expressions for all pairs of component and target value:'

    for comp in model.components:
        localpars=[]
        for par in model.parameters:
            if par.owner.name==comp.name:
                localpars.append(par)
        
        localvars=[c[0].name for c in localpars[0].context.items()]
        localmax=[c[0].max for c in localpars[0].context.items()]
        localindex=dict(zip([c[0] for c in localpars[0].context.items()],range(len(localvars))))
        LF=Logicfun(localvars,localmax)
                
        # a list with truthtables for all values for all components (all empty now):
        ttbls=[[] for c in xrange(comp.max+1)]
        # now check for every state (cmpltt contains all) which parameters are active
        for i,bstate in enumerate(LF.cmpltt): 
            for lpar in localpars:      
                for r in lpar.context.items(): # check the context, r[0] is the regulator,
                                        # r[1] the values, where it is active
                    # if one regulator is not active, parameter cant be neither, so break
                    if not ((i//LF.levprod[localindex[r[0]]])%LF.nlevs[localindex[r[0]]]) in r[1]:
                        break
                else: # if instead all regulators are active this state is
                    #added to the truthtable of the parameter
                    ttbls[partargets[lpar]].append(bstate)
        #print LF.cmpltt
        #print TTbls

        print '\nTarget values of ',comp.name,' and their conditions:'
        for j,v in enumerate(ttbls):
            # now the truthtables are translated to minimal DNFs
            primecov=LF.minimise(v) #get a prime cover
            expr=LF.writeexpr2(primecov,'brackets') # get a explicit expression of the minimal DNF
            print comp.name,'-> %d : '%j,expr
                
class Logicfun:   
    def __init__(self,comps,Max):    
        self.comps=comps
        self.Max=Max
        self.N=sum(Max)

        self.cmpltt=[]        
        self.levprod=[1]
        self.nlevs=[]
        self.chivars=['nn' for c in Max]
        for i,c in enumerate(Max):
            self.chivars[i]=(2**c-1)<<sum(Max[:i])
            self.levprod.append(self.levprod[-1]*(c+1))
            self.nlevs.append(c+1)
        for i in xrange(self.levprod[-1]):
            state=[]
            for k in xrange(len(Max)):
                state.append((i//self.levprod[k])%self.nlevs[k])

            bstate=0
            for i,s in enumerate(state):
                for j in xrange(s):
                    bstate += 1<<(sum(Max[:i])+j)
            self.cmpltt.append(bstate)
    def disjunction(self,ttList):
        disj=set([])
        for t in ttList:
            disj|=set(t)
        return disj   
    def multicomplement(self,ttbl):
        return set(self.cmpltt)-set(ttbl)
    def multisingl(self,i):
        tt=set([])
        for k in self.cmpltt:
            if k>>i&1:
                tt.add(k)
        return tt
    def minimise(self,ttbl):
        ttbl=list(ttbl)
        if len(ttbl)==0:
            return 0
        elif set(ttbl)==set(self.cmpltt):
            return 1
        else:
            primes=self.getprimesmulti(ttbl)
            cols,nrdc,nrdr=self.reducing(primes,ttbl)
            primecov=self.advprimecover(cols,primes)
            return primecov
    def getprimesmulti(self,ttbl):
        """
        diese funktion beachtet die Bedeutung der booleschen variablen die eine
        multivalue variable beschreiben, insofern, dass z.B:
        'Xconj and a>=1 or Xconj and not a>=2' zu Xconj and True == Xconj' wird
        es wird dafuer ein weiterer Fall abgefragt, bei dem dann zwei minterme
        verschmolzen werden.
        und zwar dann, wenn alles belegunggen gleich, ausser bei einer multivariable,
         bei dieser variable werden dann die dontcares vereint,d.h. alle booleschen
         variablen, die bei einer der beiden dontcare sind, sind dann auch im neuen minterm
         ein dont care. Das wars
        """
        newterms=[set([]) for i in xrange(self.N+1)]
        for i,t in enumerate(ttbl):
            newterms[self.bits(t)].add((t,t))
        eatenB=set([])
        primes=[]
        while newterms:
            #print len(newterms),'MINS_______________'
            minterms=[c.copy() for c in newterms]+[set([])]
            newterms=[]
            for i in xrange(len(minterms)-1):
                new=set([])
                eatenA=eatenB.copy()
                eatenB=set([])

                for a in minterms[i]:
                    for b in minterms[i+1]:               
                        if a[0]^a[1]==b[0]^b[1] and self.bits((a[1]^b[0])&b[0])==1:
                            new.add((a[0]&b[0],a[1]|b[1]))
                            eatenA.add(a)
                            eatenB.add(b)
                        else:    # additional possibility to merge minterms because of multivalue-implications between variables
                            for vslice in self.chivars:
                                if a[0]|vslice==b[0]|vslice and a[1]|vslice==b[1]|vslice and a[0]&b[1]==a[0] and a[1]&b[0]==b[0]:
                                    new.add((a[0]&b[0],a[1]|b[1]))
                                    eatenA.add(a)
                                    eatenB.add(b)
                #print len(minterms[i]),len(eatenA)
                primes+=[p for p in minterms[i]-eatenA]
                #print len(primes),'primes'
                #print len(new),'new'
                if new:
                    newterms.append(new)
        return primes


    def reducing(self,primes,ttbl):
        def colreduce(rows,cols,dltcols):
            deletion=False
            for i,x in enumerate(cols):
                if x and i not in dltcols:
                    for j,y in enumerate(cols[i+1:]):
                        if y and j+i+1 not in dltcols:
                            if y<=x:
                                dltcols.add(i) #delete x
                                deletion=True
                                break
                            elif x<y:
                                dltcols.add(i+j+1) #delete y
                                deletion=True
            for r in rows:
                r-=dltcols
            return deletion

        def rowreduce(rows,cols,dltrows):
            deletion=False
            for i,x in enumerate(rows):
                if x and i not in dltrows:
                    for j,y in enumerate(rows[i+1:]):
                        if y and j+i+1 not in dltrows:
                            if x<=y:
                                dltrows.add(i) #delete x
                                deletion=True
                                break
                            elif y<x:
                                dltrows.add(i+j+1) #delete y
                                deletion=True
            for c in cols:
                c-=dltrows
            return deletion

    
        M=len(ttbl)
        cols=[set([]) for c in xrange(M)]
        rows=[set([]) for c in xrange(len(primes))]
        for i,m in enumerate(ttbl):
            for j,p in enumerate(primes):
                if p[0]&m==p[0] and p[1]&m==m:
                    rows[j].add(i)
                    cols[i].add(j)

        dltcols=set([])
        dltrows=set([])
        while colreduce(rows,cols,dltcols):
            if not rowreduce(rows,cols,dltrows):
                break
        for i in dltcols:
            cols[i]=0   
        return cols,len(dltcols),len(dltrows)
    
    def advprimecover(self,cols,primes):
        def halfprimecover(columns,primes):
            game=set([0])
            sol=0
            columns.sort(key=lambda x:len(x))
            #print columns
            for column in columns:
                if column:
                    nxgame=set([])
                    for s in game:
                        new=set([])
                        for x in column:
                            if s|x==s:
                                new=set([s])
                                break
                            else:
                                for y in nxgame:
                                    if (s|x)&y==y:
                                        break
                                else:
                                    new.add(s|x)
                        nxgame|=new
                    game=sorted(list(nxgame),key=lambda x: self.bits(x),reverse=True)
            endgame=sorted(list(game),key=lambda x: (self.bits(x),x))                
            return endgame
        
        if len(primes)<=15:
            return self.primecover(cols,primes)
        columns=[[] for c in cols]
        for i,c in enumerate(cols):
            if c:
                for t in c:
                    columns[i].append(1<<t)
        m=len(columns)
        cols1=columns[:m//2]
        cols2=columns[m//2:]
        game1=halfprimecover(cols1,primes)
        game2=halfprimecover(cols2,primes)


        pairs=[(a,b) for a in game1 for b in game2]
        #pairs.sort(key=lambda x: max(self.bits(a),self.bits(b)))
        opt=float('inf')
        for a,b in pairs:
            if max(self.bits(a),self.bits(b))>=opt:
                break
            x=a|b
            size=self.bits(x)
            if size<opt:
                sol=x
                opt=size       
        prsol=[]
        for i,p in enumerate(primes):
            if sol>>i&1:
                prsol.append(p[:2])                
        return prsol
    
    def primecover(self,cols,primes):
        #print len(primes),'primes'
        columns=[[] for c in cols]
        game=set([0])
        sol=0
        for i,c in enumerate(cols):
            if c:
                for t in c:
                    columns[i].append(1<<t)
        columns.sort(key=lambda x:len(x))

        for column in columns:
            if column:
                nxgame=set([])
                for s in game:
                    new=set([])
                    for x in column:
                        if s|x==s:
                            new=set([s])
                            break
                        else:
                            for y in nxgame:
                                if (s|x)&y==y:
                                    break
                            else:
                                new.add(s|x)
                    nxgame|=new
                #game=nxgame
                game=sorted(list(nxgame),key=lambda x: self.bits(x),reverse=True)
        endgame=sorted(list(game),key=lambda x: (self.bits(x),x))
        sol=endgame[0]
        prsol=[]
        for i,p in enumerate(primes):
            if sol>>i&1:
                prsol.append(p[:2])                
        return prsol

    def bits(self,number):
        count=0
        for i in xrange(self.N):
            count+=number>>i&1
        return count

    def writeexpr2(self,primes,*args):
        if args and len(args)==1 and args[0]=='brackets': nobrck=0
        else: nobrck=1
        if primes==0:
            return 'False'
        elif primes==1:
            return 'True'
        else:
            comps=self.comps
            localMax=self.Max
            #print 'localMax:::::::::: ',localMax
            conj=[]
            for p in primes:
                lits=[]                
                for i,comp in enumerate(comps):
                    cmprange=range(sum(localMax[:i]),sum(localMax[:i+1]))
                    poslit=[]
                    neglit=[]
                    #print len(cmprange)
                    for j,k in enumerate(cmprange):
                        if j==0:
                            if p[0]>>k&1:
                                poslit=1
                            elif not p[1]>>k&1:
                                neglit=0
                                poslit=0
                                break
                        if j==len(cmprange)-1:
                            if p[0]>>k&1:
                                poslit=j+1
                                neglit=j+1
                                break
                            elif not p[1]>>k&1 and neglit==[]:
                                neglit=j
                        elif not j==0:
                            if p[0]>>k&1:
                                poslit=j+1
                            elif not p[1]>>k&1 and neglit==[]:
                                neglit=j
                    if not poslit==[]:
                        if poslit==neglit:
                            lits.append(comp+'==%d'%poslit)
                        elif not neglit==[]:
                            lits.append('%d<='%poslit+comp+'<=%d'%neglit)
                        else:
                            lits.append(comp+'>=%d'%poslit)
                    elif not neglit==[]:
                        lits.append(comp+'<=%d'%neglit)
                if nobrck:
                    conj.append(' and '.join(filter(lambda x:x,lits)))
                else:
                    conj.append('('+' and '.join(filter(lambda x:x,lits))+')')
            expr=' or '.join(conj)
            return expr    


if __name__=='__main__':
    run()
