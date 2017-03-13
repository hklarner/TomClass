
import itertools as IT
from Engine import Database
from Engine.Constraints import Parser

reload(Database)
reload(Parser)

def run():

    Db_name = 'Carbon.sqlite'
    Restriction = ''

    db = Database.Analysis(Db_name)
    db.select(Restriction)
    selected = db.count()

    print
    print 'Analysis of parameter values'
    print ' -finds values common to all parametrizations'
    print ' -finds value ranges of all parameters'
    print

    model = db.readModel()
    model.info()
    print
    
    print 'Database name:         ',"'"+Db_name+"'"
    print 'Restriction:           ', "'"+Restriction+"'"
    print 'Models in database:    ', db.size
    print 'Models selected:       ', selected

    cps = Parser.Interface(model)


    print
    print 'Ranges of parameter values:'
    for comp in model.components:
        print comp

        for p in comp.parameters:
            sql = 'SELECT DISTINCT '+str(p)+' FROM Parametrizations WHERE '+Database.SELECTION+'=1'
            db.cur.execute(sql)

            values = sorted([str(row[str(p)]) for row in db.cur])
            print (' %s:'%p).ljust(15)+','.join(values)
            
    db.close()




if __name__=='__main__':
    run()
