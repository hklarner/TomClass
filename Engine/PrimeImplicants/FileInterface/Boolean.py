
import pyparsing as PYP



def read( Lines, Verbose ):

    mLines = []
    for line in Lines:
        line = line.strip()
        if not line: continue

        name, eq = line.split(':')
        name = name.strip()
        eq = eq.strip()
        eq = parse( eq )

        lhs = name+'=1'
        mline = lhs.ljust(10)+':'+eq
        mLines.append( mline )

        if Verbose>1:
            print '  <',line
            print ' >>',mline

    return mLines


def strOperand(t):
    if t[0] in '01': # constant
        return t[0]
    return t[0]+'=1'

def strNot(t):
    return '!(' + t[0][1] + ')'

def strOperator(t):
    return '('+' '.join(t[0])+')'
        
    
            
#+'-*[]'
boolOperand = PYP.Word(PYP.alphanums+'_-/.')
boolOperand.setParseAction(strOperand)
boolExpr = PYP.operatorPrecedence( boolOperand,
    [
    ("!", 1, PYP.opAssoc.RIGHT, strNot),
    ("&", 2, PYP.opAssoc.LEFT,  strOperator),
    ("|",  2, PYP.opAssoc.LEFT, strOperator),
    ])

def parse(Equation):
    try:
        res = boolExpr.parseString(Equation, parseAll=True)[0]
    except PYP.ParseException, err:
        print err.line
        print " "*(err.column-1) + "^"
        print err


    return res
     


if __name__=='__main__':
    t = '''
Cdc20          : CycB
CycA           : ((!UbcH10 & !Rb & E2F & !Cdc20) | (!UbcH10 & !Rb & CycA & !Cdc20) | (!cdh1 & !Rb & E2F & !Cdc20) | (!cdh1 & !Rb & CycA & !Cdc20))
CycB           : (!cdh1 & !Cdc20)
CycD           : CycD
CycE           : !(Rb & E2F)
E2F            : ((!Rb & !CycB & !CycA) | (p27 & !Rb & !CycB))
Rb             : ((!CycE & !CycD & !CycB & !CycA) | (p27 & !CycD & !CycB))
UbcH10         : (!cdh1 | (UbcH10 & Cdc20) | (UbcH10 & CycB) | (UbcH10 & CycA))
cdh1           : ((!CycB & !CycA) | Cdc20 | (p27 & !CycB))
p27            : ((!CycE & !CycD & !CycB & !CycA) | (p27 & !CycD & !CycB & !CycA) | (p27 & !CycE & !CycD & !CycB))

    '''
    lines = t.split('\n')
    for line in lines:
        line=line.strip()
        if line:
            line = line.split(':')[1]
            eqs = parse( line )
            for e in eqs:
                print e
