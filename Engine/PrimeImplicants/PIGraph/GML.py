

import Attributes
import networkx as NX


def write( Graph, Fname, verbose=1):
    if not Fname[-4:]=='.gml': Fname+='.gml'
    print 'Creating',Fname+'..'
    
    NX.write_gml(Graph, Fname)

def copy_layout_GML2NX(Fname, Graph, verbose=1):
    if not Fname[-4:]=='.gml': Fname+='.gml'
    print 'importing layout from', Fname+'..'
    
    layout_graph =  NX.read_gml( Fname )
    labels = NX.get_node_attributes(layout_graph, 'label')
    _layout = NX.get_node_attributes(layout_graph, 'graphics')
    
    layout = {}
    for k,v in labels.items():
        layout[v] = {'x':_layout[k]['x'], 'y':_layout[k]['y']}

    node_names = set([])
    for n in Graph.nodes():
        if n[0]=='_' and n[1:].isdigit(): continue
        node_names.add( n[:-2] )

    if not layout_graph:
        print '   empty layout graph'
        return
    if not node_names:
        print '   empty target graph'
        return

    
    intersection = set.intersection( set(Graph.nodes()), set(layout) )
    if intersection: # exact layout, including auxillary nodes
        print '   layout from implicant graph..'
        intersection = len(intersection)
        percent=100.*intersection/Graph.order()
        print '   %.1f%%'%percent,'(%i positions)'%intersection
        NX.set_node_attributes( Graph, 'graphics', layout)
        return
        
    else:
        print '   layout from interaction graph..'
        intersection = len(node_names.intersection(layout))
        percent=100.*intersection/len(node_names)
        print '   %.1f%%'%percent,'(%i positions)'%intersection

    meta_nodes = {'_auxillary':set([])}
    for n in Graph.nodes():

        if n[0]=='_' and n[1:].isdigit():
            meta_nodes['_auxillary'].add( n )
        else:
            if not n[:-2] in meta_nodes:
                meta_nodes[n[:-2]] = set([])
            meta_nodes[n[:-2]].add( n )

    attr = {}
    # Place level nodes on circle inside components
    for name in layout:
        levels = NX.DiGraph()
        levels.add_nodes_from( meta_nodes[name] )
        circle = NX.circular_layout( levels, scale=30 )
        for n in levels.nodes():
            attr[n] = {'x':circle[n][0]+layout[n[:-2]]['x'],
                       'y':circle[n][1]+layout[n[:-2]]['y']}

    # place auxillary nodes midway between sources and targets
    for n in meta_nodes['_auxillary']:
        pred = set( [k[:-2] for k in Graph.predecessors( n )] )
        suc  = [k[:-2] for k in Graph.successors( n )].pop()
        pred = Graph.predecessors( n )
        suc  = Graph.successors( n ).pop()
        
        
        size = 1.*len(pred)
        _x = sum([attr[k]['x'] for k in pred])/size
        _y = sum([attr[k]['y'] for k in pred])/size

        w = 1. # weight of suc
        x  = (_x + w*attr[suc]['x'])/(w+1)
        y  = (_y + w*attr[suc]['y'])/(w+1)
        attr[n] = {'x':x, 'y':y}
        
    NX.set_node_attributes( Graph, 'graphics', attr)



    

