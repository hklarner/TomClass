
import subprocess
import os
import sys

from Engine.Constraints import Parser
from Engine import Database
from Engine import TransitionGraphs
from Engine import PrimeImplicants


keywords = {'Db_name'        : 'ABC.sqlite',
            'Restriction'    : 'TS1="T"'}

def run( Parameters ):
    
    for key in Parameters:
        if not key in keywords:
            print ' ** Unknown parameter: "%s"'%key
            print '    Parameters must belong to:',','.join(keywords)
            raise Exception

    Db_name         = Parameters['Db_name']
    Restriction     = Parameters['Restriction']


    db = Database.Interface( Db_name )
    selected = db.count( Restriction )
    Model = db.get_model()
    

    print
    print '---Annotation by Number of Prime Implicants'
    print 'Restriction:          ', "'"+Restriction+"'"
    print 'Models selected:      ', selected,'/',db.size
    print 'Description:           Adds a column "PIC_v" for each component v that records the number of PIs of f_v'
    print '                       and a column "PIC" which is the total complexity.'

    flag = False
    names = ['PIC_%s'%v.name for v in Model.components]+['PIC']
    for name in names:
        if name in db.property_names:
            flag = True
            db.reset_column( name )
        else:
            if name=='PIC': desc='The total number of prime implicants.'
            else: desc='The number of prime implicants of %s'%(name[5:-2])
            db.add_column( name, 'INT', desc )
    if flag: print '  Columns reset.'

    annotation_condition = ' or '.join(['PIC_%s IS NULL'%v.name for v in Model.components])
    if Restriction: annotation_condition+= ' and '+Restriction
    

    print
    print 'Starting annotations, please wait..'

    
    freqs = {}
    param, labels, rowid = db.get_row( annotation_condition )
    
    while param:

        eqs = PrimeImplicants.Equations.FromTomClass( Model, param )
        primes = eqs.compute_primes()
        
        for v in Model.components:
            sql = ' and '.join(['%s=%i'%(p,k) for p,k in param.items() if p.owner.name==v.name])
            column = 'PIC_%s'%v.name
            label = 0
            
            for a in primes[v.name]:
                label+=len(primes[v.name][a])

            ID = v.name+'_PIC='+str(label)
            if not ID in freqs: freqs[ID] = 0
            freqs[ID]+=1
            db.set_labels(sql, {column: label})
        param, labels, rowid = db.get_row( annotation_condition )

        count = db.count( annotation_condition )
        print '\rProgress: %2.3f%%'%(100.*(1-1.*count/selected)),
        sys.stdout.flush()
        

    sql = ' + '.join(['"PIC_%s"'%v.name for v in Model.components])
    db.cur.execute('UPDATE Parametrizations SET PIC = '+sql)
    db.cur.execute('SELECT Min(PIC) FROM Parametrizations')
    MinPIC = db.cur.fetchone()['Min(PIC)']
    db.cur.execute('SELECT Max(PIC) FROM Parametrizations')
    MaxPIC = db.cur.fetchone()['Max(PIC)']
    
    print
    print ' Complexities PIC_v'
    for label in sorted(freqs.keys()):
        print ("       '%s':"%label).ljust(22),freqs[label]
    for i in range(MinPIC,MaxPIC+1):
        print ' PIC=',i,'#=',db.count('PIC=%i'%i)

    db.close()








                 






    
