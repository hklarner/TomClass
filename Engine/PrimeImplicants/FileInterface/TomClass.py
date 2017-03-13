


def read( Model, Params ):
    eqs = {}
    for comp in Model.components:
        eqs[comp.name]={}
        for a in comp.range:
            eqs[comp.name][a] = Equation(comp, a, Params, Model )

    return eqs



class Equation():
    def __init__(self, Component, Value, Parametrization, Model):
        self.model  = Model 
        self.comp   = Component
        self.val    = Value
        self.params = Parametrization
        self.regulators = set([c[0].name for c in Component.regulators])

    def variables(self):
        return self.regulators

    def __repr__(self):
        if self.comp.max>1 or any([reg.max>1 for reg,thrs in self.comp.regulators]):
            return 'non-boolean (representation not implemented yet)'
        
        s= []
        for p in self.comp.parameters:
            if not self.params[p]: continue
            l=[]
            for reg,interval in p.context.items():
                if interval==(0,):   l.append('!%s'%reg.name)
                elif interval==(1,): l.append(reg.name)
            s.append('&'.join(l))
        return '|'.join(s)

    def __len__(self):
        return sys.maxint
        
    def __call__(self, Assignment):
        for p in self.comp.parameters:
            if all([Assignment[reg.name] in p.context[reg] for reg in p.context]):
                break
        return self.params[p]==self.val
