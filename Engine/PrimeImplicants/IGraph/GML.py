

import networkx as NX


def write( Graph, Fname, verbose=1):
    if not Fname[-4:]=='.gml': Fname+='.gml'
    print 'Creating',Fname+'..'

    NX.write_gml(Graph, Fname)

def copy_layout_GML2NX(Fname, Graph, verbose=1):
    if not Fname[-4:]=='.gml': Fname+='.gml'
    print 'Copying layout from', Fname+'..'
    
    g1 =  NX.read_gml( Fname )
    labels1 = NX.get_node_attributes(g1, 'label')
    n1 = set(labels1.values())
    
    nodes = set( Graph.nodes() )

    if not n1:
        print '   empty layout graph'
        return
    if not nodes:
        print '   empty target graph'
        return

    mapping = {}
    for L1 in labels1:
        for name in nodes:
            if labels1[L1]==name:
                mapping[L1] = name
                break

    intersection = len(nodes.intersection(n1))
    percent=100.*intersection/len(nodes)
    print '   %.1f%%'%percent,'(%i positions)'%intersection

    layout = NX.get_node_attributes(g1, 'graphics')
    attr = dict([  (  mapping[ID],  {'x':layout[ID]['x'],'y':layout[ID]['y']}  )   for ID in mapping])
    
    NX.set_node_attributes( Graph, 'graphics', attr)

