
import itertools as IT
from Engine import Database
import csv

reload(Database)


keywords = {'Db_name'       : 'ABC.sqlite',
            'Properties'    : ['sign_Fis_CRP','sign_cAMPCRP_CRP'],
            'Restriction'   : 'TimeSeries="T" and Attractors>1',
            'FileName'      : 'table.csv'}

def run( Parameters ):
    
    for key in Parameters:
        if not key in keywords:
            print ' ** Unknown parameter: "%s"'%key
            print '    Parameters must belong to:',','.join(keywords)
            raise Exception


    Db_name      = Parameters['Db_name']
    Properties   = Parameters['Properties']
    Restriction  = Parameters['Restriction']

    db = Database.Interface( Db_name )
    selected = db.count( Restriction )

    print
    print '---Analysis of property classes'
    if not selected:
        print 'No parametrizations selected.'
        db.close()
        return
    
    if not Properties:
        Properties = list(db.property_names)
        if not Properties:
            print "No properties in DB '"+Db_name+"'", "please add annotations."
            db.close()
            return
    
    
    if Restriction:
        print 'Restriction:         ', "'"+Restriction+"'"
    print 'Models selected:     ', selected, '/', db.size
    print 'Properties selected: ',','.join([n for n in Properties])
    print 'Label coverage'
    for prop in Properties:
        sql = prop+' IS NOT NULL'
        if Restriction: sql+= ' AND '+Restriction
        count = db.count( sql )
        print '%s %i (%2.1f%%)'%((' '+prop+':').ljust(19),count,100.*count/selected)

    
    table = []
    table.append(tuple(Properties[:]+['Size', '']))
    width = max([len(str(t)) for row in table for t in row])

    sql = 'SELECT DISTINCT '+','.join(Properties)+' FROM Parametrizations'
    if Restriction: sql+= ' WHERE '+Restriction
    db.cur.execute(sql)

    classes = []
    for row in db.cur:
        classes.append([(p, row[p]) for p in Properties])

    for Class in classes:
        table_row = []
        sqls = []

        for p, value in Class:
            width = max([len(str(value)),width])
            if value==None:
                sqls.append(p+' IS NULL')
                table_row.append('-')
            else:
                sqls.append(p+'="'+str(value)+'"')
                table_row.append(str(value))
                

        sql = ' and '.join(sqls)
        size = db.count(sql)
        table_row.append(size)
        table_row.append('%2.1f%%'%(100.*size/selected))
        table.append(tuple(table_row))
        width = max([len(str(size)),width])

    db.close()

    if 'FileName' in Parameters:
        with open(Parameters['FileName'],'w') as f:
            writer = csv.writer(f)
            writer.writerows(table)
        print 'created',Parameters['FileName']
        return

    key_func = lambda x: int(x[-1].split('.')[0])
    table = [table[0]]+sorted(table[1:], key=key_func, reverse=True)
    print    
    print 'Classes'
    for row in table:
        for value in row:
            print str(value).ljust(width),
        print

    

        
        




if __name__=='__main__':
    run()
