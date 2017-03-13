
import ast
import sys


def read( Fname, Verbose ):
    f=open(Fname, 'r')
    lines = f.readlines()
    f.close()

    primes = {}
    for line in lines:
        head, tail = line.split('::')
        n, k = head.split('=')
        if not n in primes: primes[n]={}
        k=int(k)
        primes[n][k] = ast.literal_eval(tail)

    eqs = {}
    for n in primes:
        eqs[n]={}
        for k in primes[n]:
            eqs[n][k] = Equation( primes[n][k] )

    return primes, eqs


def write( Fname, Primes ):
    p = []
    for n in sorted(Primes):
        for k in sorted(Primes[n]):
            p.append('%s=%i::%s'%(n,k,Primes[n][k]))

    f=open(Fname, 'w')
    f.write('\n'.join(p))
    f.close()

class Equation():
    def __init__(self, Primes):
        self.primes = Primes
        self.regulators = set([n for p in Primes for n in p])

    def __call__(self, Assignment):
        for p in self.primes:
            if all([ Assignment[n]==k for n,k in p.items() ]):
                return True
        return False

    def __len__(self):
        return sys.maxint
            
    def variables(self):
        return self.regulators

    def __repr__(self):
        return ''                
                




















            
