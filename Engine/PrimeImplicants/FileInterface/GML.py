
import networkx as NX
import GraphTheory

def from_NXgraph(Graph, fname, verbose):
    if not fname[-4:]=='.gml':
        fname+='.gml'
    print 'Creating',fname+'..'
    
    attr = GraphTheory.attributes_components(Graph, verbose)
    NX.set_node_attributes(Graph, 'node_type', attr)
    attr = GraphTheory.attributes_interactions(Graph, verbose)
    NX.set_edge_attributes(Graph, 'edge_type', attr)
    
    sccs = NX.strongly_connected_components(Graph)
    condensation = NX.condensation(Graph, sccs)
    layout = NX.spring_layout(condensation, iterations=100, scale=1000)
    attr = {}
    
    for i,scc in enumerate(sccs):
        for node in scc:
            attr[node] = {'x':layout[i][0],'y':layout[i][1]}

    NX.set_node_attributes(Graph, 'graphics', attr)
    NX.write_gml(Graph, fname)


def import_layout(from_fname, to_graph):
    if not from_fname[-4:]  =='.gml': from_fname +='.gml'

    print 'importing layout from', from_fname+'..'
    g1 =  NX.read_gml(from_fname)
    labels1 = NX.get_node_attributes(g1, 'label')
    n1 = set(labels1.values())
    
    g2 =    to_graph
    n2 = set(g2.nodes())

    if not n1:
        print '   empty target graph'
        return
    if not n2:
        print '   empty layout graph'
        return

    mapping = {}
    for L1 in labels1:
        for name in n2:
            if labels1[L1]==name:
                mapping[L1] = name
                break

    intersection = len(n2.intersection(n1))
    percent=100.*intersection/len(n2)
    print '   %.1f%%'%percent,'(%i positions)'%intersection

    layout = NX.get_node_attributes(g1, 'graphics')
    attr = dict([  (  mapping[ID],  {'x':layout[ID]['x'],'y':layout[ID]['y']}  )   for ID in mapping])
    
    NX.set_node_attributes(g2, 'graphics', attr)


def copy_layout(from_fname, to_fname):
    if not from_fname[-4:]  =='.gml': from_name +='.gml'
    if not to_fname[-4:]    =='.gml': to_name   +='.gml'

    print 'reading A=', from_fname,'..',
    g1 =  NX.read_gml(from_fname)
    labels1 = NX.get_node_attributes(g1, 'label')
    n1 = set(labels1.values())
    print len(n1),'nodes'
    
    print 'reading B=', to_fname,'..',
    g2 =    NX.read_gml(to_fname)
    labels2 = NX.get_node_attributes(g2, 'label')
    n2 = set(labels2.values())
    print len(n2),'nodes'

    intersection = len(n2.intersection(n1))
    percent=100.*intersection/len(n2)
    print 'B.intersect(A)=',intersection,'(%.1f%%)'%percent

    print 'copying layout..',
    mapping = {}
    for L1 in labels1:
        for L2 in labels2:
            if labels1[L1]==labels2[L2]:
                mapping[L1] = L2
                break

    layout = NX.get_node_attributes(g1, 'graphics')
    attr = dict([  (  mapping[ID],  {'x':layout[ID]['x'],'y':layout[ID]['y']}  )   for ID in mapping])
    
    NX.set_node_attributes(g2, 'graphics', attr)
    NX.write_gml(g2, to_fname)
    print 'done.'




