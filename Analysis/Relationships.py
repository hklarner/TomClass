
import itertools as IT
from Engine import Database

reload(Database)

keywords = {'Db_name'     : 'Carbon.sqlite',
            'Properties1' : ['Attractors'],
            'Properties2' : ['TimeSeries'],
            'Restriction' : ''}

def run( Parameters ):

    for key in Parameters:
        if not key in keywords:
            print ' ** Unknown parameter: "%s"'%key
            print '    Parameters must belong to:',','.join(keywords)
            raise Exception

    Db_name     = Parameters['Db_name']
    Properties1 = Parameters['Properties1']
    Properties2 = Parameters['Properties2']
    Restriction = Parameters['Restriction']


    print
    print
    print 'Analysis of [H]ypotheses, [I]mplications, [I]ndependence'
    print ' -finds relationships between two given sets of properties'
    print

    db = Database.Interface(Db_name)
    if not db.property_names:
        print "No properties in DB '"+Db_name+"'", "please add annotations."
        db.close()
        return

    for p in [Properties1, Properties2]:
        for n in p:
            if not n in db.property_names:
                print 'Property',n,"is not in '"+Db_name+"', it is automatically removed from the analysis."
        if not p:
            p = db.property_names

    Properties1 = set([p for p in Properties1 if p in db.property_names])
    Properties2 = set([p for p in Properties2 if p in db.property_names])

    if not Properties1:
        Properties1 = set(list(db.property_names))
    if not Properties2:
        Properties2 = set(list(db.property_names))




    #db.select(Restriction)
    selected = db.count(Restriction)

    print 'Database name:       ',"'"+Db_name+"'"
    print 'Restriction:         ', "'"+Restriction+"'"
    print 'Models in database:  ', db.size
    print 'Models selected:     ', selected
    print 'Properties in DB:    ',','.join([n for n in db.property_names])
    print 'Properties1:         ',','.join(Properties1)
    print 'Properties2:         ',','.join(Properties2)

    print
    print 'Label coverage'
    for p in Properties1.union(Properties2):
        sql = p+' IS NOT NULL'
        count = db.count(sql)
        print '%s %i (%2.1f%%)'%((' '+p+':').ljust(19),count,100.*count/selected)

	labels = db.get_property_labels(Properties1.union(Properties2), SQLSelection=sql)
    #labels = db.labels(Properties1.union(Properties2), Selection=True)

    hypotheses = []
    for p,v in labels.items():
        if len(v)==1:
            hypotheses.append( p+'='+str(v[0]) )
            labels.pop(p)

    independences = dict([(p,{}) for p in labels])
    implications = []
    for p1 in labels:
        for p2 in labels:
            if p1!=p2:
                for label in labels[p1]:
                    sql = 'SELECT DISTINCT '+p2+' FROM Parametrizations WHERE '+p1+'="'+str(label)+'" and '+Database.SELECTION+'=1'
                    db.cur.execute(sql)
                    rows = db.cur.fetchall()
                    if len(rows)==1:
                        implications.append( (p1+'='+str(label), p2+'='+str(rows[0][p2])) )
                    if len(rows)==len(labels[p2]):
                        if not independences[p2].has_key(p1):
                            independences[p2][p1] = []
                        independences[p2][p1].append( str(label) )
    db.close()

    equivalences = []
    for index, (a,b) in enumerate(implications):
        for c,d in implications[index:]:
            if a==d and b==c:
                equivalences.append( (a,b) )

    for a,b in equivalences:
        implications.remove( (a,b) )
        implications.remove( (b,a) )


    if hypotheses:
        print
        print 'Hypotheses:'
        for h in hypotheses:
            print '  ',h

    if implications:
        print
        print 'Implications:'
        for i in implications:
            print '  ',' => '.join(i)

    if equivalences:
        print
        print 'Equivalences:'
        for e in equivalences:
            print '  ',' <=> '.join(e)

    indeps = []
    for p1,v in independences.items():
        if not v:
            independences.pop(p1)

        for p2 in v:
            if len(independences[p1][p2])==len(labels[p2]):
                indeps.append( (p1, p2) )
            else:
                pass#print 'parial independence:',p1,'of values',independences[p1][p2],'of',p2

    if indeps:
        print
        print 'Independences:'
    while indeps:
        a,b = indeps.pop()
        if (b,a) in indeps:
            print '  ',a,'and',b,'are mutually independent.'
            indeps.remove((b,a))
        else:
            print '  ',a,'is independent of',b



    return






if __name__=='__main__':
    run()
