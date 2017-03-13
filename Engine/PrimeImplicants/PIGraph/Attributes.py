
import networkx as NX


def nodes(Graph, verbose=1):
    # attributes:
    #       primeimplicant_forcingcyclei    (i integer)
    #       primeimplicant_mSRi             (i integer)
    #       primeimplicant_percolationi     (i integer)
    #       primeimplicant_inconsistencyi   (i integer)
    pass

def edges(Graph, verbose=1):
    # attributes:
    #       primeimplicant_forcingcycle
    #       primeimplicant_mSR
    #       primeimplicant_percolation
    #       primeimplicant_inconsistency

    attr = {}
    for cycle in NX.simple_cycles( Graph ):
        for a,b in zip(cycle[:-1],cycle[1:]):
            attr[ (a,b) ] = 'primeimplicant_forcingcycle'

