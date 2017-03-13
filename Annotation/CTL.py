
import subprocess
import os
import sys

from Engine import ModelChecking
from Engine import Database

reload(ModelChecking)
reload(Database)

keywords = {'Db_name'       : 'Carbon.sqlite',
            'Restriction'   : '',
            'Property_name' : 'TimeSeries',
            'Description'   : '',
            'Formula'       : 'EF(Signal=1& CRP=0)',
            'Initial_states'        : 'Signal=1',
            'Verification_type'     : 'Forsome',
            'Fix'           : {}}

def run( Parameters ):
    
    for key in Parameters:
        if not key in keywords:
            print ' ** Unknown parameter: "%s"'%key
            print '    Parameters must belong to:',','.join(keywords)
            raise Exception

    Db_name         = Parameters['Db_name']
    Restriction     = Parameters['Restriction']
    Property_name   = Parameters['Property_name']
    Description     = Parameters['Description']
    Formula         = Parameters['Formula']
    Initial_states  = Parameters['Initial_states']
    Verification_type   = Parameters['Verification_type']
    Fix             = Parameters['Fix']


    
    db = Database.Interface( Db_name )
    selected = db.count( Restriction )
    init = Initial_states
    if not Initial_states: init='All'

    print
    print '---Annotation by CTL model checking'
    print 'Restriction:         ',  "'"+Restriction+"'"
    print 'Models selected:     ',  selected,'/',db.size
    print 'Property name:       ',  Property_name
    print 'CTL formula:         ',  Formula
    print 'Formula description: ',  Description
    print 'Initial states:      ',  init
    print 'Verification type:   ',  Verification_type
    if Fix:
        print 'Fixed components:    ',', '.join([n+'='+str(v) for n,v in Fix.items()])
    

    if Property_name in db.property_names:
        print 'Property',Property_name,'is reset.'
        db.reset_column(Property_name)
    else:
        db.add_column( Property_name, 'INT', Description )
        
    for name in Fix:
        if name in Initial_states:
            print 'Component',name,'is fixed and seems to appear in initial states spec. Please check this is correct.'

    
    annotation_condition = '"'+Property_name+'"'+' IS NULL'
    if Restriction: annotation_condition+= ' and '+Restriction
    
    Model = db.get_model()
    mc = ModelChecking.CTL( Model, Formula, Initial_states, Verification_type, Fix )

    print
    print 'Starting annotations, please wait..'
    
    freqs = {0:0,1:0}
    count = 0
    param, labels, rowid = db.get_row( annotation_condition )


    while param:
        
        count+=1
        label = 0
        if mc.check(param): label = 1
        db.set_labels('rowid=%i'%rowid, {Property_name: label} )
        freqs[label]+=1
        param, labels, rowid = db.get_row( annotation_condition )
        
        print '\rProgress: %2.3f%%'%(100.*count/selected),
        sys.stdout.flush()
    
    db.close()

    print
    print "Label '1':           ",freqs[1]
    print "Label '0':           ",freqs[0]
    





