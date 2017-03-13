

def read( Lines, verbose ):
    lowercase = False # force to read all "metabolites" in lower case.

    lines = [l.split()[0] for l in Lines]

    if lowercase:
        lines = [l.lower() for l in lines]
        
    errors = []
    DNFs = {}
    for line in lines:
        if not '=' in line:
            errors.append('ERR: no "=" in '+line+'\n')
            continue
        
        source,target = line.split('=')
        source=source.strip()
        target=target.strip()
        if not target:
            continue
        if not source:
            source = target
            
                
        if not DNFs.has_key(target):
            DNFs[target] = []

        source=source.split('+')
        DNFs[target].append(source)

    BooleanLines = []
    for k, dnf in sorted(DNFs.items(),key=lambda x: x[0]):
        s = ' | '.join(['&'.join(conjunction) for conjunction in dnf])
        BooleanLines.append( '%s : %s\n'%(k,s) )

    if verbose>-1:
        print 'equations:'.ljust(15), len(BooleanLines)
    if errors:
        for e in errors:
            print e
        print 'errors:'.ljust(15),len(errors)

    return BooleanLines
