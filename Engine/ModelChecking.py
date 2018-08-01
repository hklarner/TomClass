
import subprocess

TEMP_FNAME = 'temp.smv'
NUSMV_CMD = '/home/hannes/github/NuSMV-a/NuSMV-2.6.0/NuSMV/build/bin/NuSMV_linux64'


class Interface(object):
    def __init__(self, Model, Formula, InitialStates, VerificationType, Fix={}):

        if not NuSMV_works(NUSMV_CMD, TEMP_FNAME):
            return

        if VerificationType.lower()=='forsome':
            self.verification_str = 'is false'
            Formula = '!('+Formula+')'
        elif VerificationType.lower()=='forall':
            self.verification_str = 'is true'
        else:
            raise Exception('Input Error: Verfication type must be either "ForSome" or "ForAll", not %s.'%VerificationType)

        items = Fix.items()
        Fix = dict([(comp,v) for n,v in items for comp in Model.components if comp.name==n])

        self.smv_str = Async_SMV(Model, self.Language, Formula, VerificationType, InitialStates, Fix)

        f=open(TEMP_FNAME, 'w')
        f.write(self.smv_str)
        f.close()

    def check(self, Param):

        f=open(TEMP_FNAME, 'w')
        f.write(self.smv_str.format(Param))
        f.close()

        out = subprocess.Popen([NUSMV_CMD, TEMP_FNAME], stderr=subprocess.STDOUT, stdout=subprocess.PIPE).communicate()[0]

        if self.verification_str in out:
            return 1
        return 0

class CTL(Interface):
    Language = 'CTL'

class LTL(Interface): # seperate class for "witness-based speed up"
    Language = 'LTL'



def Async_SMV(Model, Language, Formula, VerificationType, InitialStates='', Fix={}):
    s  = 'MODULE main\n'
    s += 'DEFINE\n'
    for comp in Model.components:
        if comp in Fix:
            s +='\t%s := %i;\n'%(comp,Fix[comp])
        else:
            s +='\t%simage := \n\t\tcase\n'%comp
            for p in comp.parameters:
                condition = ' & '.join(['%s in {{%s}}'%(name, ','.join([str(v) for v in values])) for name, values in p.context.items()])
                if not condition: condition='TRUE' # for constants
                s += '\t\t\t%s: {0[%i]};\n'%(condition,p.index)
            s += '\t\t\tTRUE: 0;\n'
            s += '\t\tesac;\n'
            s += '\t%sdif := %simage - %s;\n'%(comp,comp,comp)
            s += '\tdelta%s := %sdif >0?1:%sdif<0?-1:0;\n\n'%(comp,comp,comp)

    condition = ', '.join(['(delta%s!=0)'%comp for comp in Model.components if not comp in Fix])
    s += '\tDelta := count(%s);\n\n'%condition

    s += 'VAR\n'
    for comp in Model.components:
        if not comp in Fix:
            s += '\t%s: 0..%i;\n'%(comp,comp.max)

    s += '\nASSIGN\n'
    dynamic = [comp for comp in Model.components if not comp in Fix]

    for i,comp in enumerate(dynamic):
        previous = []
        if i>0:
            previous = dynamic[:i]
        after = []
        if i<len(dynamic):
            after = dynamic[i+1:]

        s += '\tnext(%s) :=\n'%comp
        s += '\t\tcase\n'
        s += '\t\t\tdelta%s=0: %s;\n'%(comp,comp)
        if previous:
            s += '\t\t\t'+'|'.join(['next(%s)!=%s'%(p,p) for p in previous])+': %s;\n'%comp
        if after:
            s += '\t\t\t'+'|'.join(['delta%s!=0'%a for a in after])+': {{%s, %s+delta%s}};\n'%(comp,comp,comp)
        s += '\t\t\tTRUE: %s+delta%s;\n'%(comp,comp)
        s += '\t\tesac;\n'


    if InitialStates:
        s += '\nINIT '+InitialStates+'\n'

    if Language=='CTL':
        s += '\nCTLSPEC\n\t' + Formula
    elif Language=='LTL':
        s += '\nLTLSPEC\n\t' + Formula

    return s

def NuSMV_works(NusmvPath, Fname):
    f = open(Fname, 'w')
    f.write('-- Created to check if "%s" responds.'%NusmvPath)
    f.write('\nMODULE main')
    f.close()

    print ' Nusmv path:', NusmvPath
    print ' Temp file :', Fname

    p = subprocess.Popen([NusmvPath, Fname], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out = p.stdout.read()
    if not 'This is NuSMV' in out:
        print 'NuSMV path "%s"does not work.'%NusmvPath
        print 'Output:'
        print '\n\t>'.join(out.split('\n'))
        return False
    return True
