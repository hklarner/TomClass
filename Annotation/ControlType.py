
import itertools as IT
from Engine import Database
from Engine.Constraints import Parser
from Engine import PrimeImplicants

reload(Database)
reload(Parser)

keywords = {'Db_name'       : 'Carbon.sqlite',
            'Restriction'   : 'TimeSeries=1',
            'Components'    : [],
            'Display'       : 'Equations'}

def run( Parameters, Verbose=0 ):

    for key in Parameters:
        if not key in keywords:
            print ' ** Unknown parameter: "%s"'%key
            print '    Parameters must belong to:',','.join(keywords)
            raise Exception

    Db_name         = Parameters['Db_name']
    Restriction     = Parameters['Restriction']
    Components      = Parameters['Components']
    Display         = Parameters['Display']
        
    db = Database.Interface( Db_name )
    model = db.get_model()

    d = []
    for name in Components:
        hit = False
        for comp in model.components:
            if comp.name==name:
                d.append(comp)
                hit = True
                break
        if not hit:
            print '  Component',name,'is not part of the model, please check.'
    if not d:
        Components = model.components
    else:
        Components = d
        

    selected = db.count( Restriction )
    print
    print '---Annotation by component types'
    print 'Database name:       ', "'"+Db_name+"'"
    print 'Restriction:         ', "'"+Restriction+"'"
    print 'Models selected:     ', selected,'/',db.size
    print 'Components selected: ', ','.join([str(c) for c in Components])
    

    localpars = {}
    for comp in Components:
        localnames = tuple([str(p) for p in comp.parameters])
        localpars[localnames] = []
        
        sql = 'SELECT DISTINCT '+','.join(localnames)+' FROM Parametrizations'
        if Restriction: sql+=' WHERE '+Restriction
        
        db.cur.execute(sql)
        for row in db.cur:
            localpars[localnames].append(tuple([row[n] for n in localnames]))

    for comp in Components:
        if comp.name in db.property_names:
            print 'Property',comp.name,'is reset.'
            db.reset_column( comp.name )
        else:
            db.add_column(comp.name, 'int', 'Local functions of %s'%comp.name)

    for comp in Components:
        localnames = tuple([str(p) for p in comp.parameters])
        for i,localp in enumerate(localpars[localnames]):
            sql = ' and '.join([n+'='+str(v) for n,v in zip(localnames,localp)])
            if Restriction: sql+= ' and '+Restriction
            db.set_labels( sql, {comp.name: i} )

    print
    print 'Number of different controls by component:'
    if Verbose>-1:
        for comp in Components:
            localnames = tuple([str(p) for p in comp.parameters])
            print
            if Display.lower()=='parameters':
                print 'Component:',comp, 'Parameters:', localnames[0],'..',localnames[-1]
            else:
                print 'Component:',comp
            
            for i,localp in enumerate(localpars[localnames]):
                sql = ' and '.join([n+'='+str(v) for n,v in zip(localnames,localp)])
                if Restriction: sql+= ' and '+Restriction
                param, labels, rowid = db.get_row( sql )

                if Display.lower()=='parameters':
                    print ' '.join([str(v) for v in localp]),'       :',
                    print db.count( comp.name+'='+str(i) )
                else:
                    eqs = PrimeImplicants.Equations.FromTomClass( model, param)
                    m   = eqs.minimize()
                    for val in m[comp.name]:
                        if val>0:
                            if val>1: print val,':',
                            print m[comp.name][val].ljust(50),'(%i)'%(db.count( comp.name+'='+str(i) ))
                
    else:
        for comp in Components:
            sql = 'SELECT Count(DISTINCT '+comp.name+') FROM Parametrizations'
            db.cur.execute(sql)
            row = db.cur.fetchone()
            count = row['Count(DISTINCT '+comp.name+')']
            print '  ',(comp.name+':').ljust(22),count

    db.close()      


if __name__=='__main__':
    run()
