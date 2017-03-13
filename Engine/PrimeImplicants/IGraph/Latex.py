
import networkx as NX

def boundary_square(Points):
    #Points=[(x,y),(x,y)..
    if len(Points)==1:
        x,y = Points[0]
        square = [(x,y),(x+.001,y+.001)]
        return square
    
    x1,y1 = Points[0]
    x2,y2 = Points[1]
    square = [(min(x1,x2),min(y1,y2)),(max(x1,x2),max(y1,y2))]
    for x,y in Points[2:]:
        x1,y1=square[0]
        x2,y2=square[1]
        square = [(min(x1,x),min(y1,y)),(max(x2,x),max(y2,y))]
    
    return square

def boundary_polygon(Points):
    pass

def write( Graph, Fname, Parameters, verbose=1):
    if not Fname[-4:]=='.tex': Fname+='.tex'
    print 'Creating',Fname+'..'
    
    # INPUT VALUES
    OVERRIDE = {}
    if Parameters.has_key('override'):
        OVERRIDE = Parameters['override']
    FLAG_straight_edges = Parameters.has_key('straight_edges')
    FLAG_no_interaction_labels = Parameters.has_key('no_interaction_labels')
    print FLAG_no_interaction_labels
    
        
    DIMX = Parameters['dimx']  # scale dimension
    DIMY = Parameters['dimy']
    PADX = Parameters['padx']  # padding
    PADY = Parameters['pady']

    NODE_TYPES =    NX.get_node_attributes( Graph, 'node_type')
    EDGE_TYPES =    NX.get_edge_attributes( Graph, 'edge_type')
    EDGE_LABELS =   NX.get_edge_attributes( Graph, 'edge_label')
    GRAPHICS =      NX.get_node_attributes( Graph, 'graphics')

    if not any([NODE_TYPES, EDGE_TYPES, EDGE_LABELS]):
        print '  ','** missing attributes, export as GML first'
    if not GRAPHICS:
        print '  ','** missing layout, export as GML first'


    # PRINT INFORMATION
    node_count = {}
    scc_count  = {}
    
    for n,attr in NODE_TYPES.items():
        if attr[:-1]=='component_scc':
            if scc_count.has_key(attr):
                scc_count[attr]+=1
            else:
                scc_count[attr] =1
        else:
            if node_count.has_key(attr):
                node_count[attr]+=1
            else:
                node_count[attr] =1

    scc_count = sorted(scc_count.values())
    
    sccs = NX.strongly_connected_components( Graph )
    assert(sorted([len(scc) for scc in sccs if len(scc)>1]) == scc_count ) # make sure sccs really contain more than 1 node

    if verbose>0:
        print '  Node types:'
        for k,v in node_count.items():
            print '  ',k.ljust(15),':',v
        print '  ','SCCs'.ljust(15),':',','.join([str(i) for i in scc_count])


    # SCALING TO TIKZ CANVAS
    min_x,min_y = 10000,10000
    max_x,max_y = -10000,-10000
    for node in GRAPHICS:
        min_x = min(GRAPHICS[node]['x'], min_x)
        min_y = min(GRAPHICS[node]['y'], min_y)
        max_x = max(GRAPHICS[node]['x'], max_x)
        max_y = max(GRAPHICS[node]['y'], max_y)

    range_x = abs(max_x-min_x)
    range_y = abs(max_y-min_y)
    if range_x==0:range_x=0.1
    if range_y==0:range_y=0.1

    if range_x>range_y:
        factor = DIMX/range_x
    else:
        factor = DIMY/range_y

    shift_x = abs(min_x)
    shift_y = abs(min_y)
    if verbose>0:
        print '   scaling to x,y:',DIMX,DIMY
        print '   factor: %.2f'%factor

    for node in GRAPHICS:
        GRAPHICS[node]['x']=factor*(shift_x+GRAPHICS[node]['x'])
        GRAPHICS[node]['y']=DIMY-factor*(shift_y+GRAPHICS[node]['y'])

    def NormId(name):
        for a,b in [('_','0000'),('-','1111'),('/','2222'),('.','3333')]:
            name = name.replace(a,b)
        return name
    def NormLabel(name):
        name = name.replace('_','\\_')
        return name


    # ADD COMPONENTS TO TIKZ
    s = '\n\\begin{tikzpicture}\n'
    for node in Graph.nodes():
        ntype = NODE_TYPES[node]
        if ntype[:-1] == 'component_scc': ntype = 'component_scc'  # e.g. "component_scc2" -> "component_scc"

        if node in OVERRIDE:
            if 'additional_ntypes' in OVERRIDE[node]:
                ntype = ','.join([ntype]+OVERRIDE[node]['additional_ntypes'])
        
        s+= '   \\node[%s] at (%.1f,%.1f) (%s) {%s};\n'%(ntype,GRAPHICS[node]['x'],GRAPHICS[node]['y'],
                                                         NormId(node),NormLabel(node))
    s += '\n'


    # ADD BACKGROUND NODES TO TIKZ    
    s += '\\begin{pgfonlayer}{background}\n'
    points = {}
    for node in GRAPHICS:
        ntype = NODE_TYPES[node]
        if ntype == 'component_transient': continue

        ntype = ntype[10:]                  # e.g. "component_input" -> "input"
        
        if not points.has_key(ntype):
            points[ntype] = []

        points[ntype].append((GRAPHICS[node]['x'],GRAPHICS[node]['y']))
        


    counter = 0
    for ntype in points:
        A,B = boundary_square(points[ntype])
        s+= '   \\coordinate (A%i) at (%.1f,%.1f);\n'%(counter,A[0]-PADX,A[1]-PADY)
        s+= '   \\coordinate (B%i) at (%.1f,%.1f);\n'%(counter,B[0]+PADX,B[1]+PADY)
        if ntype[:-1]=='scc': ntype='scc'   # e.g. "scc4" -> "scc"
        s+= '   \\node[auxillary_bgd_%s, fit=(A%i)(B%i)] {};\n'%(ntype,counter,counter)
        counter+=1


    # ADD INTERACTIONS TO TIKZ
    for source,target in Graph.edges():

        # BEND
        x1, y1 = GRAPHICS[source]['x'],GRAPHICS[source]['y']
        x2, y2 = GRAPHICS[target]['x'],GRAPHICS[target]['y']

        bend = 'edge[]'
        if source!=target and not FLAG_straight_edges:
            bend = 'edge[bend right]'
            if abs(  x2-x1  )<.8 or abs(  y2-y1  )<.8:
                if not Graph.has_edge(target, source):
                    bend = '--'
            elif x1<x2:
                bend = 'edge[bend left]'
            
        # OVERRIDE
        if (  source,target  ) in OVERRIDE:
            ovr = OVERRIDE[(  source,target  )]
            if 'draw' in ovr:
                draw = ovr['draw']
            if 'bend' in ovr:
                bend = ovr['bend']

        etype  = EDGE_TYPES[(source,target)]
        
        if FLAG_no_interaction_labels:
            s+= '   \\draw[%s] (%s) %s (%s);\n'%(etype, NormId(source), bend, NormId(target))
        else:
            elabel = 'node[label_%s]{}'%EDGE_LABELS[(source,target)]
            s+= '   \\draw[%s,interaction_%s] (%s) %s %s (%s);\n'%(etype, EDGE_LABELS[(source,target)], NormId(source), bend, elabel, NormId(target))

    s += '\\end{pgfonlayer}\n'
    s += '\\end{tikzpicture}'
    f = open( Fname, 'w' )
    f.write(s)
    f.close()
