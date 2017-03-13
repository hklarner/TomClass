
import networkx as NX
import math



def write( Graph, Fname, Parameters, verbose=1):
    if not Fname[-4:]=='.tex': Fname+='.tex'
    print 'Creating',Fname+'..'
    
    # INPUT VALUES
    OVERRIDE = {}
    if Parameters.has_key('override'):
        OVERRIDE = Parameters['override']
    DIMX = Parameters['dimx']  # scale dimension
    DIMY = Parameters['dimy']
    PADX = Parameters['padx']  # padding
    PADY = Parameters['pady']

    #NODE_TYPES =    NX.get_node_attributes( Graph, 'node_type')
    #EDGE_TYPES =    NX.get_edge_attributes( Graph, 'edge_type')
    #EDGE_LABELS =   NX.get_edge_attributes( Graph, 'edge_label')
    GRAPHICS =      NX.get_node_attributes( Graph, 'graphics')
    FLAG_labels = Parameters.has_key('labels')

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


    # LEVELS
    s = '\n\\begin{tikzpicture}\n'
    for node in Graph.nodes():
        if node[0]=='_' and node[1:].isdigit(): # auxillary node
            pass
        else: # level node
            s+= '   \\node[implicant_level%s] at (%.2f,%.2f) (%s) {};\n'%(node[-1:],GRAPHICS[node]['x'],GRAPHICS[node]['y'],NormId(node))
    s += '\n'




    # META NODES
    meta_nodes = {'_auxillary':set([])}
    for n in Graph.nodes():

        if n[0]=='_' and n[1:].isdigit():
            meta_nodes['_auxillary'].add( n )
        else:
            if not n[:-2] in meta_nodes:
                meta_nodes[n[:-2]] = set([])
            meta_nodes[n[:-2]].add( n )
            
    s += '\\begin{pgfonlayer}{background}\n'
    
    for node in meta_nodes:
        if node=='_auxillary': continue
        size = 1.*len(meta_nodes[node])
        x = sum([GRAPHICS[n]['x'] for n in meta_nodes[node]])/size
        y = sum([GRAPHICS[n]['y'] for n in meta_nodes[node]])/size

        label = ''
        if FLAG_labels: label = 'label=%s'%node
        s+= '   \\node[implicant_metanode] at (%.2f,%.2f) [%s] {};\n'%(x,y,label)
        # with label:
        # s+= '   \\node[primeimplicant_metanode,label={[label distance=2pt]90:%s}] at (%.2f,%.2f) {};\n'%(node,x,y)

    # ARCS
    counter =0
    for node in Graph.nodes():

        succs  = Graph.successors( node )

        if not (node[0]=='_' and node[1:].isdigit()): # not auxillary node
            for suc in succs:
                if suc==node: continue
                if not (suc[0]=='_' and suc[1:].isdigit()): # prime of length 1
                    s+= '   \\draw[implicant, pi_head] (%s) -- (%s);\n'%(NormId(node),NormId(suc))
            continue

        # node is auxillary, e.g. "_12" so we have a hyperarc
        suc = succs.pop() # there is a unique successor, the arrow head
        pred = [p for p in Graph.predecessors( node )] # the sources of the hyperarc    
        
        # average predecessor point
        size = 1.*len(pred)
        av_x = sum([GRAPHICS[n]['x'] for n in pred])/size
        av_y = sum([GRAPHICS[n]['y'] for n in pred])/size
        #s+= '   \\node[] at (%.2f,%.2f) (av) {};\n'%(av_x,av_y)

        # auxillary point
        aux_x = GRAPHICS[node]['x']
        aux_y = GRAPHICS[node]['y']
        

        # target point
        tar_x = GRAPHICS[suc]['x']
        tar_y = GRAPHICS[suc]['y']

        angle = Angle(av_x,av_y,aux_x,aux_y) #...
        angle = Angle(aux_x,aux_y,tar_x,tar_y)
        
        if tar_x>aux_x: angle+=180.
        
        # loop implicant with only 1 other predecessor: move auxillary point!
        if len([p for p in pred if p !=suc])==1:
            
            
            alpha = Angle(tar_x, tar_y, aux_x, aux_y)
            d = math.sqrt(abs(tar_x-aux_x)**2+abs(tar_y-aux_y)**2)

            #s+= '   \\node[fill=gray] at (%.2f,%.2f) (aux) {};\n'%(aux_x,aux_y)

            p1_x = aux_x
            p1_y = aux_y
            aux_x = tar_x+ d*math.cos(alpha+80.)
            aux_y = tar_y+ d*math.sin(alpha+80.)
            if p1_y<aux_y: angle+=180.

            #s+= '   \\node[fill=red] at (%.2f,%.2f) (aux) {};\n'%(aux_x,aux_y)
           
            # edge from auxillary point to suc
            s+= '   \\draw[implicant] (%.2f,%.2f) edge[in=%.2f, out=%.2f, pi_head] (%s);\n'%(aux_x,aux_y, angle+180., angle+180., NormId(suc))
        else:
            # straight line from auxillary point to suc
            s+= '   \\draw[implicant, pi_head] (%.2f,%.2f) -- (%s);\n'%(aux_x,aux_y, NormId(suc))


        #s+= '   \\draw[thick,dashed,red,label=angle] (aux) -- ++(%.2f:5mm);\n'%angle
        #s+= '   \\node[circle,fill=purple] at (%.2f,%.2f) (WP) {};\n'%(aux_x,aux_y)
        #s+= '   \\draw[dashed,dark green] (WP) -- ++(%.2f:5mm);\n'%angle
        
        
        
        # edges from predecessors to auxillary point
        for p in pred:
            pred_x = GRAPHICS[p]['x']
            pred_y = GRAPHICS[p]['y']

            # out-angle from individual preds to average point
            angle2 = Angle(pred_x,pred_y,av_x,av_y) #...
            angle2 = Angle(pred_x,pred_y,aux_x,aux_y)
            if pred_x > aux_x: angle2 += 180.
            #if pred_y > av_y: angle -= 180.

            #s+= '   \\draw[thick,dashed,blue,label=angle2] (%s) -- ++(%.2f:5mm);\n'%(NormId(p),angle2)
            s+= '   \\draw[implicant] (%s) edge[in=%.2f, out=%.2f] (%.2f,%.2f);\n'%(NormId(p), angle, angle2, aux_x, aux_y)

            

    # loops for constants
    for node in Graph.nodes_with_selfloops():
        s+= '   \\draw[implicant, pi_loop, pi_head] (%s) edge[] (%s);\n'%(NormId(node),NormId(node))


    s += '\\end{pgfonlayer}\n'
    s += '\\end{tikzpicture}'
    f = open( Fname, 'w' )
    f.write(s)
    f.close()
    return
    ### STOP ###

    counter = 0
    for ntype in points:
        A,B = boundary_square(points[ntype])
        s+= '   \\coordinate (A%i) at (%.2f,%.2f);\n'%(counter,A[0]-PADX,A[1]-PADY)
        s+= '   \\coordinate (B%i) at (%.2f,%.2f);\n'%(counter,B[0]+PADX,B[1]+PADY)
        if ntype[:-1]=='scc': ntype='scc'   # e.g. "scc4" -> "scc"
        s+= '   \\node[auxillary_bgd_%s, fit=(A%i)(B%i)] {};\n'%(ntype,counter,counter)
        counter+=1


    # ADD INTERACTIONS TO TIKZ
    for source,target in Graph.edges():

        # BEND
        x1, y1 = GRAPHICS[source]['x'],GRAPHICS[source]['y']
        x2, y2 = GRAPHICS[target]['x'],GRAPHICS[target]['y']

        bend = 'edge[]'
        if source!=target:
            if abs(  x2-x1  )<.8 or abs(  y2-y1  )<.8:
                bend = '--'
            elif x1<x2:
                bend = 'edge[bend right]'
            else:
                bend = 'edge[bend left]'
            
        # OVERRIDE
        if (  source,target  ) in OVERRIDE:
            ovr = OVERRIDE[(  source,target  )]
            if 'draw' in ovr:
                draw = ovr['draw']
            if 'bend' in ovr:
                bend = ovr['bend']

        etype  = EDGE_TYPES[(source,target)]
        elabel = 'node[label_%s]{}'%EDGE_LABELS[(source,target)]
        s+= '   \\draw[%s,interaction_%s] (%s) %s %s (%s);\n'%(etype, EDGE_LABELS[(source,target)], NormId(source), bend, elabel, NormId(target))

    s += '\\end{pgfonlayer}\n'
    s += '\\end{tikzpicture}'
    f = open( Fname, 'w' )
    f.write(s)
    f.close()
    

def Angle(x1,y1,x2,y2):
    if x2-x1==0:
        if y2>y1:
            a = +90
        else:
            a = -90
    else:
        m = 1.*(y2-y1)/(x2-x1)
        a = math.atan(m)*180./math.pi

    return a
