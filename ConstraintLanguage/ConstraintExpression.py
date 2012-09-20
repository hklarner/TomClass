import pyparsing as PYP

import Core
import Transitions
import EdgeLabel
import Multiplex
import Inequality
import Identity
reload(Core)
reload(Transitions)
reload(EdgeLabel)
reload(Multiplex)
reload(Inequality)
reload(Identity)


class ConstraintNode(object):
    def __init__(self, toks):
        self.root = toks[0]
        
    def __iter__(self):
        if isinstance(self.root, Core.AndNode):
            for a in self.root.args:
                yield ConstraintNode([a])
        else:
            yield self
                

    def __repr__(self):
        return str(self.root)

    def __call__(self, Assignment):
        return self.root(Assignment)

    def used_variables(self):
        return self.root.used_variables()
    
    def initialize(self, Model):
        self.root.initialize(Model)


Predicate = Transitions.Subgraph ^ Transitions.Path ^ EdgeLabel.EdgeLabel ^ Multiplex.Multiplex ^ Inequality.InequalityAbs ^ Inequality.InequalityRel ^ Identity.Identity
Formula = PYP.operatorPrecedence(Predicate,[(Core.Not, 1, PYP.opAssoc.RIGHT, Core.NotNode),
                                                       (Core.And,  2, PYP.opAssoc.LEFT, Core.AndNode),
                                                       (Core.Or, 2, PYP.opAssoc.LEFT, Core.OrNode),
                                                       (Core.Implies, 2, PYP.opAssoc.LEFT, Core.ImpliesNode)])
Formula.setParseAction(ConstraintNode)
