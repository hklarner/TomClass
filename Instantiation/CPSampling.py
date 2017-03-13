
import os

from Engine import Models
from Engine import Database
from Engine.Constraints import Parser
from Engine.Constraints import NiemeyerSolver
from Engine.Constraints import Automation

keywords   = {'Db_name'     : 'ABC.sqlite',
              'Samples'     : 1000,
              'Components'  : [('A',2), ('B',2), ('C',2)],
              'Interactions': [('A','A',(1,)),('A','B',(2,)),
                               ('B','C',(1,)),('C','B',(2,))],
              'Constraint'  : 'Activating(A,A,1) and Observable(A,B,2)'}

def run( Parameters, verbose=-1 ):
    
    for key in Parameters:
        if not key in keywords:
            print ' ** Unknown parameter: "%s"'%key
            print '    Parameters must belong to:',','.join(keywords)
            raise Exception


    Db_name      = Parameters['Db_name']
    Samples      = Parameters['Samples']
    Components   = Parameters['Components']
    Interactions = Parameters['Interactions']
    Constraint   = Parameters['Constraint']

    Model = Models.Interface(Components, Interactions)

    if verbose>0:
        print
        print '---CP based uniform sampling'
      
    if os.path.isfile(Db_name):
        if verbose>-1: print 'Database',Db_name,'exists already. File replaced.'
        if 1:
            os.remove(Db_name)
            Database.New(Db_name, Model)
    else:
        Database.New(Db_name, Model)
        
    if verbose>-1:
        print 'Created database:      ',"'"+Db_name+"'"
        Model.info()
    cps = Parser.Interface(Model)
    cps.parse(Constraint)

    if verbose>-1: 
        print
        print 'Constraint:'
        print Constraint
        print
        print 'Samples:               ',Samples
    db = Database.Interface( Db_name )
    count = 0
    
    for param in cps.samples(Samples):
        db.insert_row( param )
        count+=1

    db.close()

    if verbose>-1: 
        print
        print 'Solutions:             ',count
    


