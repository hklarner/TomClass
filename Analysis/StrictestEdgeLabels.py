
import itertools as IT
from Engine import Database
from Engine.Constraints import Parser

reload(Database)
reload(Parser)

keywords = {'Db_name'       : 'ABC.sqlite',
            'Interactions'  : [('Fis','Fis',1),('','Fis',1)],
            'Restriction'   : 'TimeSeries="T" and Attractors>1'}


def run( Parameters ):

    for key in Parameters:
        if not key in keywords:
            print ' ** Unknown parameter: "%s"'%key
            print '    Parameters must belong to:',','.join(keywords)
            raise Exception

    Db_name         = Parameters['Db_name']
    Interactions    = Parameters['Interactions']
    Restriction     = Parameters['Restriction']

    db = Database.Interface(Db_name)
    selected = db.count(Restriction)
    model = db.get_model()

    print
    print '---Strictest edge labels'
    print 'Database name:         ',"'"+Db_name+"'"
    print 'Restriction:           ', "'"+Restriction+"'"
    print 'Models selected:     ',  selected,'/',db.size
    print 'Interactions selected: ',
    if not Interactions:
        print 'All'
        for a,b,trs in model.interactions:
            for t in trs:
                Interactions.append( (a,b,t) )
    else:
        print ','.join([a+'-'+str(i)+'->'+b for a,b,i in Interactions]) 

    # encoding + -
    SEL_mapping = {'00':        'not observable',
                   '01':        'inhibiting only',
                   '10':        'activating only',
                   '11':        'dual',
                   '0001':      'not activating',
                   '0010':      'not inhibiting',
                   '0011':      'dual xor not observable',
                   '0110':      'monotonous',
                   '0111':      'inhibiting',
                   '1011':      'activating',
                   '000110':    'not dual',
                   '000111':    'not activating only',
                   '001011':    'not inhibiting only',
                   '011011':    'observable',
                   '00011011':  'free'}

    cps = Parser.Interface(model)


    print
    print 'Strictest edge labels:'
    for a,b,t in Interactions:
        signature = ''
        
        cps.parse( 'NotActivating(%s,%s,%i) and NotInhibiting(%s,%s,%i)'%(a,b,t,a,b,t) )
        condition = cps.toSQL()
        if Restriction: condition+=' and '+Restriction
        sql = 'SELECT rowid FROM Parametrizations WHERE '+condition+' LIMIT 1'
        db.cur.execute(sql)
        row = db.cur.fetchone()
        if row:
            signature += '00'

        cps.parse( 'NotActivating(%s,%s,%i) and Inhibiting(%s,%s,%i)'%(a,b,t,a,b,t) )
        condition = cps.toSQL()
        if Restriction: condition+=' and '+Restriction
        sql = 'SELECT rowid FROM Parametrizations WHERE '+condition+' LIMIT 1'
        db.cur.execute(sql)
        row = db.cur.fetchone()
        if row:
            signature += '01'

        cps.parse( 'Activating(%s,%s,%i) and NotInhibiting(%s,%s,%i)'%(a,b,t,a,b,t) )
        condition = cps.toSQL()
        if Restriction: condition+=' and '+Restriction
        sql = 'SELECT rowid FROM Parametrizations WHERE '+condition+' LIMIT 1'
        db.cur.execute(sql)
        row = db.cur.fetchone()
        if row:
            signature += '10'

        cps.parse( 'Activating(%s,%s,%i) and Inhibiting(%s,%s,%i)'%(a,b,t,a,b,t) )
        condition = cps.toSQL()
        if Restriction: condition+=' and '+Restriction
        sql = 'SELECT rowid FROM Parametrizations WHERE '+condition+' LIMIT 1'
        db.cur.execute(sql)
        row = db.cur.fetchone()
        if row:
            signature += '11'

        if signature:
            print a.rjust(10)+'-(%i)->'%t+b.ljust(10)+SEL_mapping[signature]
        else:
            print 'Error for',a,b,t

    db.close()




if __name__=='__main__':
    run()
