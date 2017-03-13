
import subprocess
import os
import sys
import heapq

from Engine import Database
from Engine import TransitionGraphs

reload(Database)
reload(TransitionGraphs)

keywords = {'Db_name'           : 'ABCDE.sqlite',
            'Restriction'       : '',
            'Property_name'     : 'Lytic',
            'Property_type'     : 'text',
            'Description'       : '.',
            'TimeSeries'        : [ {'c1':0,'c2':0,'cro':0,'vN':0},
                                    {'c1':0,'c2':0,'cro':2,'vN':1},
                                    {'c1':0,'c2':0,'cro':2,'vN':0},
                                    {'c1':0,'c2':0,'cro':3,'vN':0},
                                    {'c1':0,'c2':0,'cro':2,'vN':0}],
            'Monotony'          : [ {'c1':True,'c2':True,'cro':True,'vN':True},
                                    {'c1':True,'c2':True,'cro':True,'vN':True},
                                    {'c1':False,'c2':False,'cro':False,'vN':False},
                                    {'c1':False,'c2':False,'cro':False,'vN':False}]
            }

def run( Parameters ):

    Db_name         = Parameters['Db_name']
    Restriction     = Parameters['Restriction']
    Property_name   = Parameters['Property_name']
    Property_type   = Parameters['Property_type']
    Description     = Parameters['Description']
    TimeSeries      = Parameters['TimeSeries']
    Monotony        = Parameters['Monotony']

    print
    print 'Annotation by Saschas A*-graph traversal'
    print ' -checks a time series with monotony spec'
    print

   
    db = Database.Modification(Db_name)
    if Property_name in db.property_names:
        print 'Property',Property_name,'is reset.'
        db.reset(Property_name)
    db.close()


    db = Database.Analysis(Db_name)
    db.select(Restriction)
    selected = db.count()
    Model = db.readModel()
    db.close()
    Model.info()

    print
    print 'Database name:       ',"'"+Db_name+"'"
    print 'Restriction:         ', "'"+Restriction+"'"
    print 'Models in database:  ', db.size
    print 'Models selected:     ', selected
    print 'Property name:       ',Property_name
    print 'Time Series:         '
    for row in TimeSeries:
        print row
    print 'Monotony'
    for row in Monotony:
        print row

    db = Database.Annotation(Db_name)
    db.newProperty(Property_name, Property_type, Description)
    db.select(Property_name, Restriction)

    
    print
    print 'Starting annotations, please wait..'
    freqs = {'F':0,'T':0}
    count = 0
    walker = Walker(Model)
    walker.set_timeseries(TimeSeries, Monotony)

    param, labels, rowid = db.next()
    while param:
        count+=1
        label = 'F'
        walker.set_parameterset(param)
        if walker.is_compatible():
            label = 'T'
        db.label('rowid=%i'%rowid, label)
        freqs[label]+=1
        param, labels, rowid = db.next()
        print '\rProgress: %2.3f%%'%(100.*count/selected),
        sys.stdout.flush()
    
    db.close()
    print
    print "Label 'T':           ",freqs['T']
    print "Label 'F':           ",freqs['F']
    print


class Walker():
    '''Provides methods to check TimeSeries directly in a State Transition Graph.'''
        
    def __init__(self, Model): # Model
        self.M = Model
        self.Names = [c.name for c in Model.components]
        self.ASTG = TransitionGraphs.Asynchronous(Model)
        self._timeseries = None
        self._visited = set([])


    def emptymonotonicityMatrix(self):
        '''Returns an appropriate all-False monotonicity matrix for the ``self._timeseries``.'''
        m = []
        for i in range( len(self._timeseries)-1 ):
            m.append([ False for v in self.Names ] )
        return m
    
    def set_parameterset(self, ps):
        '''Sets a new ParameterSet.'''
        self.ASTG.setParams(ps)
        
    def set_timeseries(self, timeseries, monotonicity = list()):
        '''Sets a new timeseries and monotonicity. The time series must at least contain two states.'''

        # input check
        assert(len(timeseries)>1)
        for dic in timeseries:
            assert(type(dic) == type(dict()))
            for v in self.Names: 
                assert(v in dic and type(dic[v]) == type(1))
        
        self._timeseries = []
        for state in timeseries:
            self._timeseries.append(  tuple([state[n] for n in self.Names])  )
        

        if not monotonicity:
            self._monotonicity = self.emptymonotonicityMatrix()
        else:
            # input check
            assert(len(monotonicity) == len(self._timeseries)-1)
            for dic in monotonicity:
                assert(type(dic) == type(dict()))
                for v in self.Names:
                    assert(v in dic and type(dic[v]) == type(True))

            self._monotonicity = []
            for mon in monotonicity:
                self._monotonicity.append(  tuple([monotonicity[n] for n in self.Names])  )
            self._monotonicity = monotonicity
                

    def is_compatible(self):
        '''Searches a monotone path along the states in time series.'''

        # as long as set_timeseries() was used, the timeseries and monotonicity matrix are correct.
        assert(len(self._timeseries)>1)

        for i in range(len(self._timeseries)-1):
            # clear visited list
            self._visited = set([])
            if not self.Astar(self._timeseries[i], self._timeseries[i+1], self._monotonicity[i]):
                return False

        return True

    def Astar(self, startState, targetState, monotonicity):
        '''A best-first search from state `startState` to `targetState`.'''

        HEAP = []
        d = 0
        for a,b in zip(startState,targetState):
            d += abs(a-b)
        
        heapq.heappush(HEAP, (d, startState))

        while HEAP:
            (d,state) = heapq.heappop(HEAP)
            if state == targetState:
                return True
            
            self._visited.add(state)

    
            for suc in self.ASTG.successors(state):
                if suc in self._visited:
                    continue

                d=0
                comp_index = 0
                for v1,v2 in zip(state,suc):
                    if v2>v1:
                        if targetState[comp_index]>v1:
                            heapq.heappush(HEAP, (d-1,suc))
                        elif not monotonicity[comp_index]:
                            heapq.heappush(HEAP, (d+1,suc))

                    elif v2<v1:
                        if targetState[comp_index]<v1:
                            heapq.heappush(HEAP, (d-1,suc))
                        elif not monotonicity[comp_index]:
                            heapq.heappush(HEAP, (d+1,suc))

                    comp_index +=1

        return False




if __name__=='__main__':
    run()
    
