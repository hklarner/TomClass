
import pyparsing as PYP
import xml.etree.ElementTree as ET
import itertools as IT



# GINsim formula parsing



def read( Fname, Verbose=0 ):

    tree        = ET.parse(Fname)
    root        = tree.getroot()
    graph       = root.find('graph')
    nodes       = graph.iter('node')
    edges       = graph.iter('edge')

    version     = '2.9'
    sep         = ':'
    GINOperand = PYP.Word(PYP.alphanums+'_-/.:')

    for n in graph.iter('node'):
        if n.attrib.has_key('basevalue'):
            version = '2.3'
            sep     = '_'
            GINOperand = PYP.Word(PYP.alphanums+'-/.')
        break

    def strNot(t):
        return '!(' + t[0][1] + ')'
    def strOperator(t):
        return '('+' '.join(t[0])+')'
    
    GINformula = PYP.operatorPrecedence( GINOperand,
        [
        ("!", 1, PYP.opAssoc.RIGHT, strNot),
        ("&", 2, PYP.opAssoc.LEFT,  strOperator),
        ("|",  2, PYP.opAssoc.LEFT, strOperator),
        ])

    
    if Verbose>0: print 'Assumed GINsim file version:',version

    regulators = {}
    components = {}
    for n in graph.iter('node'):
        name = n.attrib['id']
        regulators[name] = set([])
        if name in components:
            print 'duplicate component in file! check', name
            raise Exception
        components[name] = int(n.attrib['maxvalue'])

    interactions = {}
    
    edge_by_id  = {}
    for e in graph.iter('edge'):
        edge_by_id[e.attrib['id']] = e
        
        From = e.attrib['from']
        To   = e.attrib['to']
        Min  = int(e.attrib['minvalue'])
        if not From in interactions: interactions[From]={}
        if not To in interactions[From]: interactions[From][To] = []
        interactions[From][To].append(Min)
        regulators[To].add( From )
        
    for e in interactions:
        for f in interactions[e]:
            interactions[e][f] = tuple(sorted(interactions[e][f]))

    # main loop preperation
    Results   = {}
    for name, Max in components.items():
        Results[name] = {}
        for j in range(Max+1):
            Results[name][j]=[]

    # main loop
    for n in graph.iter('node'):
        name        = n.attrib['id']

        #Input node?
        if version=='2.9':
            if n.attrib.has_key('input'):
                if n.attrib['input']=='true':
                    assert(n.attrib['maxvalue']=='1')
                    Results[name][0]=[name+'=0']
                    Results[name][1]=[name+'=1']
                    continue

        #verify my assumption about syntax in GIN2.3
        if version=='2.3' and '_' in name:
            print 'names in version 2.3 must not contain "_". check:',name
            raise Exception
            
        #Basevalue
        basevalue   = 0
        if version=='2.3':
            # example: <node id="N2" basevalue="0" maxvalue="1">
            assert(  n.attrib.has_key('basevalue')  )
            basevalue = int(n.attrib['basevalue'])
        else:
            if n.findall('parameter'):        
                for p in n.findall('parameter'):
                    if not p.attrib.has_key('idActiveInteractions'):
                        basevalue = int(p.attrib['val'])
                        break
                
        # Defined by formulae
        if n.findall('value'): # <value val="2">
            for formula in n.findall('value'):
                target  = int(formula.attrib['val'])
                expr    = formula.find('exp').attrib['str']
                
                if version=='2.3':  # <exp str="MASS & MBF_SBF"/>
                    print "version2.3 parsing not implemented yet!"
                else:               # <exp str="(G0:1 | G0:5) & G2"/>

                    
                    def GinAction(t):
                        if ':' in t[0]:
                            src, Min = t[0].split(':')
                            Min   = int(Min)
                            index = interactions[src][name].index(Min)
                            Max   = components[src]+1
                            if index<len(interactions[src][name])-1:
                                Max = interactions[src][name][index+1]

                        else: # pseudo boolean
                            src=t[0]
                            Min = interactions[src][name][0]
                            Max = components[src]+1
                                    
                        interval = range(Min,Max)
                        if len(interval)==1: # save a bracket for parsing :)
                            return '%s=%i'%(src,interval[0])
                        return '('+'|'.join([ '%s=%i'%(src,i) for i in interval ])+')'

                    
                    GINOperand.setParseAction(GinAction)
                    try:
                        res = GINformula.parseString( expr, parseAll=True )[0]
                    except PYP.ParseException, err:
                        print err.line
                        print " "*(err.column-1) + "^"
                        print err

                    Results[name][target].append( res )
                    #if Verbose>0: print name, target, res
            

        # Defined by parameters
        elif n.findall('parameter'):

            hit_basevalue = False
            for p in n.findall('parameter'):
                target = int(p.attrib['val'])
                terms = []
                
                # Basevalue parameter?
                if not p.attrib.has_key('idActiveInteractions'):
                    hit_basevalue = True
                    if not regulators[name]:
                        terms.append('1')
                    for reg in regulators[name]:
                        Min = 0
                        Max = interactions[reg][name][0]
                        interval = range(Min,Max)
                        terms.append( '('+'|'.join([ '%s=%i'%(reg,i) for i in interval ])+')'  )

                # Normal parameter.
                else:

                    active = p.attrib['idActiveInteractions']
                    active = active.strip()
                    active = active.split()

                    inactive = list(regulators[name])
                    for ID in active:
                        e = edge_by_id[ID]
                        From = e.attrib['from']
                        inactive.remove(From)
                        
                        Min = int(e.attrib['minvalue'])
                        index = interactions[From][name].index(Min)
                        Max   = components[From]+1
                        if index<len(interactions[From][name])-1:
                            Max = interactions[From][name][index+1]
                        interval = range(Min,Max)
                        
                        terms.append( '('+'|'.join([ '%s=%i'%(From,i) for i in interval ])+')'  )

                    for From in inactive:
                        Max = interactions[From][name][0] # first threshold
                        interval = range(Max)

                        terms.append( '('+'|'.join([ '%s=%i'%(From,i) for i in interval ])+')'  )

                terms = '&'.join( terms )
                Results[name][target].append( terms )

            if not hit_basevalue:
                target = 0
                terms = []
                if not regulators[name]:
                    terms.append('1')
                for reg in regulators[name]:
                    Min = 0
                    Max = interactions[reg][name][0]
                    interval = range(Min,Max)
                    terms.append( '('+'|'.join([ '%s=%i'%(reg,i) for i in interval ])+')'  )

                if Verbose>2: print 'Assume basevalue 0 for %s.'%name
                terms = '&'.join( terms )
                Results[name][target].append( terms )                
                

        missing = [k for k in Results[name] if not Results[name][k]]
        if missing:
            if 0 in missing:
                for k in missing:
                    if k!=0:
                        Results[name][k]=['0']
            else:
                missing.pop()
                for k in missing:
                    Results[name][k]=['0']

    Lines = []
    for name in sorted(Results):
        negated = []
        for target in sorted(Results[name], reverse=1):
            if Results[name][target]:
                term = '|'.join( Results[name][target] )
                negated.append( '!(%s)'%term )
                if target == 0:
                    negated = '&'.join(negated)
                    term = '|'.join([term,negated])

                Lines.append( '%s=%i:  %s'%(name,target,term) )

    if Verbose>0: print 'Read',len(Lines),'equations.'

    if Verbose>1:
        for line in Lines:
            print line
    
    return Lines
