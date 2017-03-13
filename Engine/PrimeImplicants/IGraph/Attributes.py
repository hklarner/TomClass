
import networkx as NX

def components(Graph, verbose=0):
    # attributes:
    #       component_const
    #       component_input
    #       component_transient
    #       componnet_scci (i integer)
    #       component_output
    
    attr = dict([(n,'component_transient') for n in Graph.nodes()])
    for node in Graph.nodes():
        pred    = [p for p in Graph.predecessors(node) if not p==node]
        suc     = [p for p in Graph.successors(node) if not p==node]
        if not pred:
            if node in Graph.predecessors(node):
                attr[node] = 'component_input'
            else:
                attr[node] = 'component_const'
        elif not suc:
            attr[node] = 'component_output'

    counter = 0
    sccs = NX.strongly_connected_components(Graph)
    
    for scc in sccs:
        if len(scc)>1:
            name = 'component_scc%i'%counter
            for node in scc:
                attr[node] = name
            counter+=1

    if verbose>0:
        print '    components:'
        counter = {}
        for name in attr:
            tag = attr[name][attr[name].find('_')+1:]
            if not tag in counter:
                counter[tag] = 0
            counter[tag]+=1

        printer = {}
        printer['sccs'] = []
        for tag in counter:
            if 'scc'==tag[:3]:
                printer['sccs'].append( str(counter[tag]) )
            else:
                printer[tag] = counter[tag]
        printer['sccs'] = str(len(printer['sccs']))+' #:'+','.join(printer['sccs'])

        for tag in printer:
            print '    ',tag.ljust(10),printer[tag]

        print '    ','total'.ljust(10),Graph.order()

    return attr

def interactions(Graph, verbose=0):
    # attributes:
    #       interaction_inputloop
    #       interaction_outputloop
    #       interaction_internal
    #       interaction_internal_loop
    #       interaction_transient
    #       interaction_transient_loop
    #       interaction_crosstalk

    topology = components(Graph)
    attr = {}
    for s,t in Graph.edges():
        # LOOP
        if s==t:
            if topology[s]          == 'component_input':
                value = 'interaction_inputloop'
            elif topology[s]          == 'component_output':
                value = 'interaction_outputloop'
            elif topology[s][:-1]   == 'component_scc':
                value = 'interaction_internal_loop'
            elif topology[s]        == 'component_transient':
                value = 'interaction_transient_loop'
            else:
                print 'Interaction',s,t,'has unknown loop:',topology[s]
                raise Exception
        # NON-LOOP
        else:
            if topology[s]=='component_transient' and topology[t]=='component_transient':
                value = 'interaction_transient'
            elif topology[s]==topology[t]:
                value = 'interaction_internal'
            else:
                value = 'interaction_crosstalk'

        attr[(s,t)] = value

    if verbose>0:
        print '    interactions:'
        counter = {}
        for name in attr:
            tag = attr[name][attr[name].find('_')+1:]
            if not tag in counter:
                counter[tag] = 0
            counter[tag]+=1

        for tag in counter:
            print '    ',tag.ljust(10),counter[tag]
        
    return attr
