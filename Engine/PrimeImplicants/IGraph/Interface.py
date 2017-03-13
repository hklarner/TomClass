

import GML
import Latex
import networkx as NX
import itertools as IT
import Attributes



class New():
    def __init__(self, Equations, Primes, Verbose):
        if Verbose>-1: print 'Creating interaction graph..'
        
        names = Primes.keys()
        _max  = dict([(n,max(Primes[n])) for n in names])
        
        graph = NX.DiGraph()
        graph.add_nodes_from( names )
        labels = {}

        # Computes all interactions, thresholds and signs, from the prime implicants.
        # The idea is to perturb each prime implicant and compare the functions obtained
        # by substituting the original and perturbed implicants.
        for name in names:

            function = TargetFunction( Equations, name )
            _vars    = set([])
            for v in Equations[name]:
                _vars.update(Equations[name][v].variables())

            for val in Primes[name]:
                if not val: continue # dont want threshold==0
                
                for p in Primes[name][val]:

                    
                    used  = p.keys()
                    free  = set( _vars ).difference( used )
                    free  = sorted(list(free))
                        
                    for k in p:

                        state       = dict(p)
                        state_inc   = dict(p)
                        state_dec   = dict(p)
                        pos         = False
                        neg         = False
                        
                        for values in IT.product(*[range(_max[n]+1) for n in free]):

                            state.update(dict(zip(free,values)))
                            state_inc.update(dict(zip(free,values)))
                            if p[k]+1 in Equations[name]: state_inc[k] = p[k]+1
                            state_dec.update(dict(zip(free,values)))
                            if p[k]-1 in Equations[name]: state_dec[k] = p[k]-1

##                            if name=='LFY':
##                                print 'Eqn:     ',Equations[name][val]
##                                print '%i-Prime: '%val,p
##                                print 'x:       ',state
##                                print 'x+:      ',state_inc
##                                print 'x-:      ',state_dec
                            
                            assert( Equations[name][val](state)  )

                            if not pos:
                                if function(state) < function(state_inc):
##                                    if name=='LFY':
##                                        print "pos"
##                                        print "function(state) < function(state_inc)",function(state),function(state_inc)
                                    pos = True
                                elif function(state_dec) < function(state):
##                                    if name=='LFY':
##                                        print "pos"
##                                        print "function(state_dec) < function(state)",function(state_dec) , function(state)
                                    pos = True
                            if not neg:
                                if function(state) > function(state_inc):
##                                    if name=='LFY':
##                                        print "neg"
##                                        print "function(state) > function(state_inc)",function(state), function(state_inc)
                                    neg = True
                                elif function(state_dec) > function(state):
##                                    if name=='LFY':
##                                        print "neg"
##                                        print "function(state_dec) > function(state)",function(state_dec) , function(state)
                                    neg = True
##                            if name=='LFY':
##                                print "function(state_dec) ? function(state)",function(state_dec) , function(state)
##                                print "function(state) ? function(state_inc)",function(state),function(state_inc)
                            if neg and pos:
                                break

                        if pos or neg:
                            if not (k,name) in labels:
                                labels[(k,name)] = {}
                            if not val in labels[(k,name)]:
                                labels[(k,name)][val] = set([])
                            if pos:
                                labels[(k,name)][val].add( 'plus' )
                            if neg:
                                labels[(k,name)][val].add( 'minus' )
        
        for k,name in labels:
            if max(Equations[name])==1: # Boolean regulator, need no threshold
                l = ','.join([''.join(sorted( labels[(k,name)][v] ,reverse=True))        for v in labels[(k,name)] ])
            else:
                l = ','.join([''.join(sorted( labels[(k,name)][v] ,reverse=True))+str(v) for v in labels[(k,name)] ])
            graph.add_edge( k, name, edge_label = l )

        self.graph = graph
                
        if Verbose>0:
            display_mapping = {'plus':'+','minus':'-', 'plusminus':'+-'}
            L = max([len(n) for n in names])
            for s,t,d in graph.edges(data=True):
                if d['edge_label'] not in display_mapping:
                    sign = ','.join([  display_mapping[x[:-1]]+x[-1] for x in d['edge_label'].split(',') ])
                else:
                    sign = display_mapping[d['edge_label']]
                print '  ',s.ljust(L+2),'--(',sign,')-->',t




        if Verbose>0:
            print '   adding node attributes'
        attr = Attributes.components( self.graph, Verbose)
        NX.set_node_attributes( self.graph, 'node_type', attr)
        
        if Verbose>0:
            print '   adding edge attributes'
        attr = Attributes.interactions( self.graph, Verbose)
        NX.set_edge_attributes( self.graph, 'edge_type', attr)

        if Verbose>0:
            print '   adding node positions'
        sccs = NX.strongly_connected_components( self.graph )
        condensation = NX.condensation( self.graph , sccs)
        layout = NX.spring_layout(condensation, iterations=100, scale=1000)
        
        attr = {}
        for i,scc in enumerate(sccs):
            for node in scc:
                attr[node] = {'x':layout[i][0],'y':layout[i][1]}

        NX.set_node_attributes( self.graph, 'graphics', attr)

    def export_as_gml(self, Fname, Verbose):
        GML.write( self.graph, Fname, Verbose )

    def import_layout(self, Fname, Verbose):
        GML.copy_layout_GML2NX( Fname, self.graph, Verbose )

    def export_as_tex(self, Fname, Parameters, Verbose):
        Latex.write( self.graph, Fname, Parameters, Verbose)

    









def TargetFunction(Equations, Name):
    # Generates the integer valued "target function" from the boolean equations.
    def wrapper(x):
        hit = False
        for val in Equations[Name]:
            if Equations[Name][val](x):
                if hit: # Overlap
                    print '  **Error: Overlap for target function of %s.'%Name
                    print val, x
                    raise Exception
                hit = val
        if not isinstance(hit,int): # Not covering
            print '  **Error: Target function of %s does not cover all states.'%Name
            print val, x
            raise Exception
        return hit
    return wrapper
























