
import subprocess
import os
import sys

from Engine.Constraints import Parser
from Engine import Database

reload(Database)


keywords = {'Db_name'        : 'ABC.sqlite',
            'Restriction'    : 'TS1="T"',
            'Property_name'  : 'Attractors',
            'Property_type'  : 'int',
            'InitialStates'  : '',
            'Description'    : ''}

def run( Parameters, CustomAlgorithm ):
    
    for key in Parameters:
        if not key in keywords:
            print ' ** Unknown parameter: "%s"'%key
            print '    Parameters must belong to:',','.join(keywords)
            raise Exception

    Db_name         = Parameters['Db_name']
    Restriction     = Parameters['Restriction']
    Property_name   = Parameters['Property_name']
    Property_type   = Parameters['Property_type']
    Description     = Parameters['Description']
    InitialStates   = ''
    if 'InitialStates' in Parameters: InitialStates = Parameters['InitialStates']

    db = Database.Interface( Db_name )
    Model = db.get_model()
    states=[]
    if InitialStates: states=Parser.InitialStates(Model,InitialStates)
    
    selected = db.count( Restriction )
    if Property_name in db.property_names:
        print 'Property',Property_name,'is reset.'
        db.reset_column(Property_name)
    else:
        db.add_column( Property_name, 'INT', Description )


    annotation_condition = '"'+Property_name+'"'+' IS NULL'
    if Restriction: annotation_condition+= ' and '+Restriction

    print
    print '---Custom Algorithm'
    print 'Restriction:          ', "'"+Restriction+"'"
    print 'Models selected:      ', selected, '/', db.size
    print 'Property name:        ', Property_name
    print 'Property description: ', Description
    if states:
        print 'Initial states:       ', InitialStates[:min(20,len(InitialStates))],'(',len(states),')'
    print
    print 'Starting annotations, please wait..'
    
    freqs = {}
    count = 0
    param, labels, rowid = db.get_row( annotation_condition )
    
    while param:
        
        count+=1
        labels = CustomAlgorithm( Model, param, labels, states )

        ID = ','.join(['%s=%s'%item for item in sorted(labels.items())])
        if not ID in freqs:
            freqs[ID] = 0

        freqs[ID]+=1
        
        db.set_labels('rowid=%i'%rowid, labels)
        param, labels, rowid = db.get_row( annotation_condition )

        print '\rProgress: %2.3f%%'%(100.*count/selected),
        sys.stdout.flush()


    
    db.close()
    print
    for label in sorted(freqs.keys()):
        print ("Label '%s':"%label).ljust(22),freqs[label]


if __name__=='__main__':
    run()
    
