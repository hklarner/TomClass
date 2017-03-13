
import networkx as NX

Info = 'Assigns an integer ID that represent the isomorphy class of asynchronous STG.'
class new():
    def __init__(self):
        self.classes = []
        
    def Call(self, Model, Parameters, Labels, States ):
        graph = NX.DiGraph()

        for state in States:
            for b in Model.async_successors(Parameters, state):
                graph.add_edge( a, b )

        i=0
        hit = False
        for i, gclass in enumerate(self.classes):
            if NX.is_isomorphic( graph, gclass ):
                hit = True
                break

        if hit:
            return i
        else:
            self.classes.append( graph )
            return i+1
    
