
import ConstraintLanguage.ConstraintExpression as CEXP
import pyparsing

reload(CEXP)

import RegulatoryGraphs
reload(RegulatoryGraphs)

TEMP_FNAME = 'temp.smv'

class Interface(object):
    def __init__(self, Model):
        self.property_name = 'CTL_1'
        self.property_description = 'This is a model checking classifier.'
        self.property_type = 'int'
        self.model = Model

    def compute_label(self, Param):
        # write smv
        # call nusmv
        # get result
        # get trace
        pass


def Asynchronous_SMV(Model):
    s  = 'MODULE main\n'
    s += 'DEFINE\n'
    for comp in Model.components:
        s +='\t%simage := \n\t\tcase\n'%comp
        for context in comp.contexts:
            condition = ' & '.join(['%s in {{%s}}'%(name, ','.join([str(v) for v in values])) for name, values in context.intervals.items()])
            s += '\t\t\t%s: {%i};\n'%(condition,context.index)
        s += '\t\t\tTRUE: 0;\n'
        s += '\t\tesac;\n'
        s += '\t%sdifference := %simage - %s;\n'%(comp,comp,comp)
        s += '\t%ssign := %sdifference >0?1:%sdifference<0?-1:0;\n\n'%(comp,comp,comp)

    condition = '&'.join(['%ssign=0'%comp for comp in Model.components])
    s += '\tfixpoint := %s?1:0;\n\n'%condition



    s += 'VAR\n'
    for comp in Model.components:
        s += '\t%s: 0..%i;\n'%(comp,comp.max+20)

    s += '\nASSIGN\n'
    Max = len(Model.components)-1
    for i,comp in enumerate(Model.components):
        s += '\tnext(%s) :=\n'%comp
        s += '\t\tcase\n'
        condition = '&'.join(['fixpoint=0']+['next({0})={0}'.format(prev) for prev in Model.components[:i]])
        if i<Max:
            s += '\t\t\t%s:'%condition
            s += '{{%s, %s+%ssign}};\n'%(comp,comp,comp)
        else:
            s += '\t\t\t%s: %s+%ssign;\n'%(condition,comp,comp)
        s += '\t\t\tTRUE: %s;\n'%comp
        s += '\t\tesac;\n\n'

    print s
    print s.format(*range(30))
    return
        
    s += 'CTLSPEC !(%s)'%self._CTL




if __name__=='__main__':
    model = RegulatoryGraphs.Boolean4()
    c = Interface(model)
    Asynchronous_SMV(model)
    
