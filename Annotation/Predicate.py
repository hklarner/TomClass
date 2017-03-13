


from Engine import Database
from Engine.Constraints import Parser
from Engine.Constraints import Automation

reload(Automation)
reload(Database)
reload(Parser)

keywords = {'Db_name'       : 'example.sqlite',
            'Restriction'   : '',
            'Property_name' : 'B_requires_A',
            'Specification' : 'Some(vA=0,vB = 0) of Observable(vA,vB,1)',
            'Description'   : 'A compound predicate.'}
                


def run( Parameters ):

    Db_name         = Parameters['Db_name']
    Restriction     = Parameters['Restriction']
    Property_name   = Parameters['Property_name']
    Specification   = Parameters['Specification']
    Description     = Parameters['Description']

    db = Database.Interface( Db_name )
    Model = db.get_model()

    if Property_name in db.property_names:
        print 'Property',Property_name,'is reset.'
        db.reset_column(Property_name)
    else:
        db.add_column(Property_name, 'int', Description)
    
    annotation_condition = '"'+Property_name+'"'+' IS NULL'
    if Restriction: annotation_condition+= ' and '+Restriction

    print
    print '---Annotation by a predicates'
    print 'Database name:       ',"'"+Db_name+"'"
    print 'Restriction:         ', "'"+Restriction+"'"
    print 'Models in database:  ', db.count(annotation_condition),'/',db.size

    
    cps = Parser.Interface(Model)
    cps.parse(Specification)
    sql = cps.toSQL()
    
    db.set_labels(sql, {Property_name:'1'})
    db.set_labels('not (%s)'%sql, {Property_name:'0'})

    T=db.count(Property_name+'=1')
    F=db.count(Property_name+'=0')
    selected = db.count( Restriction )
    db.close()

    print 'Models selected:     ', selected, '/', db.size
    print 'Name:                ', "'"+Property_name+"'"
    print 'Description:         ', Description
    print 'Specfication:        ', "'"+Specification+"'"
    print "Label '1':           ", T
    print "Label '0':           ", F


    
