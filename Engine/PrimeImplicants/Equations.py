
import FileInterface
import QMC
import IGraph
import PIGraph
import LPSolver


class Interface():
    minimized = ''
    
    def minimize(self):
        self.minimized = QMC.MyQuine.minimize( self.equations )
        return self.minimized

    def compute_primes(self, Verbose):
        self.primes = QMC.MyQuine.primes( self.equations, Verbose )
        return self.primes

    def compute_igraph(self, Verbose):
        if not hasattr(self, 'primes'): self.compute_primes(Verbose)
        self.igraph = IGraph.Interface.New( self.equations, self.primes, Verbose )
        return self.igraph

    def compute_pigraph(self, Verbose):
        if not hasattr(self, 'primes'): self.compute_primes(Verbose)
        self.pigraph = PIGraph.Interface.New( self.primes )
        return self.pigraph

    def compute_branchingtree(self, Verbose):
        if not hasattr(self, 'primes'): self.compute_primes(Verbose)
        LPSolver.compute_branchingtree( Primes=self.primes, Region={}, Verbose=Verbose )

    def save_primes(self, Fname):
        if not hasattr(self, 'primes'): self.compute_primes(Verbose=-1)
        print 'Saving primes as "%s"..'%Fname

        FileInterface.Primes.write( Fname, self.primes )

    def save_smv(self, Fname, InfluenceReduction=[], UseTrans=True, Verbose=0):
        # UseTrans= transition based encoding of asynchronicity
        if not hasattr(self, 'primes'): self.compute_primes(Verbose=-1)
        FileInterface.SMV.Primes_to_SMV( Primes=self.primes, Fname=Fname, InfluenceReduction=InfluenceReduction, UseTrans=UseTrans, Verbose=Verbose )

        
                

    def save(self, Fname):
        print 'Saving network as "%s"..'%Fname

        # not tested for FromTomClass.

        # Minimize
        # if not hasattr(self, 'minimized'): self.minimize(Verbose)
        
        s = ''
        for name in sorted(self.equations):
            for val in reversed(sorted(self.equations[name])):
                s+=(name+'='+str(val)).ljust(15)+':  '
                if self.minimized:
                    if len(self.minimized[name][val])<len(self.equations[name][val]):
                        s+=self.minimized[name][val]
                    else:
                        s+=str(self.equations[name][val])
                else:
                    s+=str(self.equations[name][val])
                s+='\n'
                    
            s+='\n'
        
        f=open( Fname, 'w' )
        f.write( s )
        f.close()

    def save_stg(self, Fname, Type):
        assert( Type in ['async', 'sync'] )

        def async_successors(Components, Parameters, State):
            succs = set([])
            fixpoint = True
            for comp in Components:
                for p in comp.parameters:
                    if all([State[reg.index] in p.context[reg] for reg in p.context]):
                        break

                if State[comp.index] == Parameters[p]:
                    continue
                
                fixpoint = False
                delta = -1
                if State[comp.index] < Parameters[p]:
                    delta = 1

                suc = list(State[:])
                suc[comp.index]+= delta
                succs.add(tuple(suc))

            if fixpoint:
                succs.add(tuple(State[:]))

            return succs


class FromLines(Interface):
    def __init__(self, Lines, CheckSemantics, Verbose):
        Equations = FileInterface.Parser.System.read( Lines, CheckSemantics, Verbose)
        
        self.equations = Equations


class FromFile(Interface):
    def __init__(self, Fname, CheckSemantics, Verbose ):
        Lines       = FileInterface.Reader.Open( Fname, Verbose )
        Equations   = FileInterface.Parser.System.read( Lines, CheckSemantics, Verbose )
        
        self.equations = Equations


class FromPrimes(Interface):
    def __init__(self, Fname, Verbose):
        Primes, Equations = FileInterface.Primes.read( Fname, Verbose )
    
        self.primes     = Primes
        self.equations  = Equations
        

class FromTomClass(Interface):
    def __init__(self, Model, Params ):
        Equations = FileInterface.TomClass.read( Model, Params )

        self.equations = Equations

    
        
        

    


