
import CNA
import Boolean
import GINsim


def Open( Fname, Verbose ):

    f = open(Fname)
    lines = f.readlines()
    f.close()

    filetype = Fname.split('.')[1].lower()
    
    if filetype == 'cna':
        if Verbose>-1: print 'Opening',Fname,'as CNA file..'
        BooleanLines = CNA.read( lines, Verbose )
        return Boolean.read( BooleanLines, Verbose )
        
    elif filetype =='txt':        

        if '=' in ''.join(lines) or '>' in ''.join(lines) or '<' in ''.join(lines):
            if Verbose>-1: print 'Opening',Fname,'as MyFormat file..'
            lines = [l.strip() for l in lines if l.strip()]
            return lines

        else:
            if Verbose>-1: print 'Opening',Fname,'as Boolean-Equations file..'
            return Boolean.read( lines, Verbose )

    elif 'gin' in filetype:
        if Verbose>-1: print 'Opening',Fname,' as GINsim file..'
        return GINsim.read( Fname, Verbose )
    else:
        print ' ** File extension in "%s" not recognized.'%Fname
        raise Exception
        
    
    
