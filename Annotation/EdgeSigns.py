


from Engine import Database
from Engine.Constraints import Parser
from Engine.Constraints import Automation

reload(Automation)
reload(Database)
reload(Parser)


def run( Parameters ):

    Db_name         = Parameters['Db_name']
    Interactions    = Parameters['Interactions']
    Restriction     = Parameters['Restriction']

    db = Database.Interface(Db_name)
    Model = db.get_model()

    if not Interactions:
        Interactions = Model.interactions

    print
    print 'Annotation by interaction signs'
    print 'Restriction:         ', "'"+Restriction+"'"
    print 'Interactions:        ', Interactions

    Properties = []
    cps = Parser.Interface(Model)
    for a,b,ts in Interactions:
        for t in ts:
            
            Property_type = 'text'
            if len(ts)==1:
                Property_name = 'sign_%s_%s'%(a,b)
            else:
                Property_name = 'sign_%s_%s_%i'%(a,b,t)
            Properties.append(Property_name)

            if Property_name in db.property_names:
                print 'Property',Property_name,'is reset.'
                db.reset_column(Property_name)
            else:
                db.add_column( Property_name, 'TEXT', 'Sign of %s %i %s'%(a,t,b) )

            annotation_condition = Property_name+' IS NULL'
            if Restriction: annotation_condition+= ' and '+Restriction

            cps.parse('ActivatingOnly(%s,%s,%i)'%(a,b,t))
            sql = cps.toSQL()
            db.set_labels(annotation_condition+' and '+sql, {Property_name:'"+"'})
            cps.parse('InhibitingOnly(%s,%s,%i)'%(a,b,t))
            sql = cps.toSQL()
            db.set_labels(annotation_condition+' and '+sql, {Property_name:'"-"'})
            cps.parse('NotObservable(%s,%s,%i)'%(a,b,t))
            sql = cps.toSQL()
            db.set_labels(annotation_condition+' and '+sql, {Property_name:'"None"'})
            cps.parse('Activating(%s,%s,%i) and Inhibiting(%s,%s,%i)'%(a,b,t,a,b,t))
            sql = cps.toSQL()
            db.set_labels(annotation_condition+' and '+sql, {Property_name:'"+-"'})
    
    selected = db.count( Restriction )
    for prop in Properties:
        sql = prop+' IS NOT NULL'
        count = db.count(sql)
        print '%s %i (%2.1f%%)'%((' '+prop+':').ljust(19),count,100.*count/selected)
    db.close()



if __name__=='__main__':
    run()
    
