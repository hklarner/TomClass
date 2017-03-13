
import sys
import itertools as IT
from Engine import Database
from Engine import PrimeImplicants

reload(Database)


keywords = {'Db_name'       : 'ABC.sqlite',
            'Restriction'   : 'TimeSeries="T" and Attractors>1',
            'FileName'      : 'model.txt'}

def run( Parameters ):
    
    for key in Parameters:
        if not key in keywords:
            print ' ** Unknown parameter: "%s"'%key
            print '    Parameters must belong to:',','.join(keywords)
            raise Exception


    Db_name      = Parameters['Db_name']
    Restriction  = Parameters['Restriction']
    FileName     = Parameters['FileName']

    db = Database.Interface( Db_name )
    selected = db.count( Restriction )
    Model  =db.get_model()

    if not selected:
        print 'No parametrizations selected.'
        return
    

    print
    print '---Export as text file'
    print 'Database name:       ',  "'"+Db_name+"'"
    print 'Restriction:         ',  "'"+Restriction+"'"
    print 'Models selected:     ',  selected,'/',db.size
    
    param, labels, rowid = db.get_row( Restriction )

    eqs = PrimeImplicants.Equations.FromTomClass( Model, param )
    eqs.minimize()
    eqs.save
    net.save( FileName, verbose=2 )

    db.close()






                                  
