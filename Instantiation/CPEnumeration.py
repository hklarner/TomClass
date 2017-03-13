
import os

from Engine import Models
from Engine import Database
from Engine.Constraints import Parser
from Engine.Constraints import NiemeyerSolver
from Engine.Constraints import Automation


keywords = {'Db_name'       : 'ABC.sqlite',
            'Components'    : [('v1',2), ('v2',2), ('v3',2)],
            'Interactions'  : [('v1','v1',(1,)),('v1','v2',(2,)),
                               ('v2','v3',(1,)),('v3','v2',(2,))],
            'Constraint'    : 'Activating(v1,v1,1) and Observable(v1,v2,2)'}

def run( Parameters, Verbose=0 ):
    
    for key in Parameters:
        if not key in keywords:
            print ' ** Unknown parameter: "%s"'%key
            print '    Parameters must belong to:',','.join(keywords)
            raise Exception


    Db_name      = Parameters['Db_name']
    Components   = Parameters['Components']
    Interactions = Parameters['Interactions']
    Constraint   = Parameters['Constraint']

    Model = Models.Interface(Components, Interactions)

    if Verbose>-1:
        print
        print '---CP Enumeration by Initial Constraints'
        print 'Created database:      ',  "'"+Db_name+"'"
        Model.info()
    
    if os.path.isfile(Db_name):
        if Verbose>-1: print 'Database',Db_name,'exists already. File replaced.'
        os.remove(Db_name)
    Database.New(Db_name, Model)
    


    cps = Parser.Interface(Model)
    cps.parse(Constraint)

    if Verbose>-1:
        print
        print 'Constraint:'
        print Constraint
        print
        print 'Enumerating, please wait..'
    db = Database.Interface( Db_name )
    count = 0
    
    for param in cps.solutions( Verbose ):
        db.insert_row( param )
        count+=1

    db.close()
    if Verbose>-1: print 'Solutions:             ', count

