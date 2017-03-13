

import networkx as NX
import GML
import Latex


class New():
    def __init__(self, Primes ):
        self.primes = Primes
        graph  = NX.DiGraph()

        counter = 0
        for name in Primes:
            for k in Primes[name]:
                graph.add_node( name+'_%i'%k )

                for prime in Primes[name][k]:
                    if not prime: continue # empty prime = constant function
                    
                    if len(prime)>1:
                        graph.add_node( '_%i'%counter )
                        for n,l in prime.items():
                            graph.add_edge( n+'_%i'%l, '_%i'%counter )
                        graph.add_edge( '_%i'%counter, name+'_%i'%k )
                        counter+=1
                    else:
                        n,l = prime.items().pop()
                        graph.add_edge( n+'_%i'%l, name+'_%i'%k )

        self.graph = graph


    def export_as_gml(self, Fname, Verbose):
        GML.write( self.graph, Fname, Verbose )

    def import_layout(self, Fname, Verbose):
        GML.copy_layout_GML2NX( Fname, self.graph, Verbose )

    def export_as_tex(self, Fname, Parameters, Verbose):
        Latex.write( self.graph, Fname, Parameters, Verbose)
