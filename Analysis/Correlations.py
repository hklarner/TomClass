
import itertools as IT
from Engine import Database

reload(Database)

def run():

    Db_name = 'Carbon.sqlite'
    Property = 'SuperCoiling'
    Correlation_set = []
    Restriction = ''
    Minimal = True


    print
    print
    print 'Analysis of Correlations'
    print ' -finds correlations between a property and a given correlation superset'
    print

    db = Database.Analysis(Db_name)
    if not db.property_names:
        print "No properties in DB '"+Db_name+"'", "please add annotations."
        db.close()
        return

    if not Property:
        print 'Please name the property you are interested in.'
        db.close()
        return

    if not Property in db.property_names:
        print 'Property '+"'"+Property+"'",'is not in',Db_name
        print 'Choose one of',','.join(db.property_names)
        db.close()
        return

    for p in Correlation_set:
        if not p in db.property_names:
            print 'Property',p,"is not in '"+Db_name+"', it is automatically removed from the analysis."
    Correlation_set = [p for p in Correlation_set if p in db.property_names and p!=Property]

    if not Correlation_set:
        Correlation_set = list(db.property_names)
        Correlation_set.remove(Property)

    if len(Correlation_set)<2:
        print 'Correlation set, currently',Correlation_set,'must contain at least two properties, please add some.'
        db.close()
        return
        

    db.select(Restriction)
    selected = db.count()

    model = db.readModel()
    model.info()
    print
    
    print 'Database name:        ',"'"+Db_name+"'"
    print 'Restriction:          ', "'"+Restriction+"'"
    print 'Models in database:   ', db.size
    print 'Models selected:      ', selected
    print 'Properties in DB:     ',','.join([n for n in db.property_names])
    print 'Property:             ',Property
    print 'Correlation superset: ',','.join(Correlation_set)
    print 'Find minimal sets:    ', Minimal

    print
    print 'Label coverage'
    for p in Correlation_set+[Property]:
        sql = p+' IS NOT NULL'
        count = db.count(sql)
        print '%s %i (%2.1f%%)'%((' '+p+':').ljust(19),count,100.*count/selected)


    
    #labels = db.labels(Properties1.union(Properties2), Selection=True)


    correlations = []
    hit=False
    for r in range(2,len(Correlation_set)+1):
        if hit and Minimal:
            break
        
        func = {}
        for C in IT.combinations(Correlation_set,r):
            props = C+(Property,)
            sql = 'SELECT DISTINCT '+','.join(props)+' FROM Parametrizations WHERE '+Database.SELECTION+'=1'
            db.cur.execute(sql)
            
            for row in db.cur:
                key = tuple([row[p] for p in C])
                if key in func:
                    if func[key]!=row[Property]:
                        func = {}
                        break
                func[key] = row[Property]
                
            if func:
                hit=True
                correlations.append(  sorted(C)  )
    db.close()
            
    if correlations:
        print
        print 'Correlations:'
        for c in correlations:
            print '  ',Property,'correlates with','{'+','.join(c)+'}'
    else:
        print
        print 'Found no correlations for',Property,'in',Correlation_set
    print
            
    



if __name__=='__main__':
    run()
