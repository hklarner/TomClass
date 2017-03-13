

import sys
import itertools as IT
import random as RND

import Instantiation
import Annotation
import Analysis
from Engine import Database
from Engine import ModelChecking as MCheck
import time



UPDATE = 'asynchronous'

DBNAME = 'example1.sqlite'
FNAMECSV = 'example1.csv'

create                  = 1

annotate_compatible     = 0
annotate_upfunctions    = 0
annotate_attractors     = 0



analyse_classes         = 0
export_csv              = 0
analyse_relationships   = 0
analyse_strictestlabel  = 0

RESTRICTION             = ''
CLASSES                 = []
RELATIONSHIPS1          = []
RELATIONSHIPS2          = []

    

def run():
    if create:

        parameters = {'Db_name'         : DBNAME,
                      'Components'      : [('v1',1),
                                           ('v2',2),
                                           ('v3',3)],
                      'Interactions'    : [('v1','v2',(1,)),
                                           ('v2','v1',(1,)),
                                           ('v2','v3',(2,)),
                                           ('v3','v1',(1,)),
                                           ('v3','v2',(2,)),
                                           ('v3','v3',(3,))]}

        clauses = [ 'Some(v1>=0,v1,=,0)',
                    'Some(v1>=0,v1,=,1)',
                    'Some(v1>=0,v2,=,0)',
                    'Some(v1>=0,v2,=,1)',
                    'Some(v1>=0,v2,=,2)',
                    'Some(v1>=0,v3,=,0)',
                    'Some(v1>=0,v3,=,1)',
                    'Some(v1>=0,v3,=,2)',
                    'Some(v1>=0,v3,=,3)',
                    ]
        
        parameters['Constraint'] = ' and '.join( clauses )
                      
        Instantiation.CPEnumeration.run( parameters )

    if not create:
        db = Database.Interface(DBNAME)
        model = db.get_model()
        model.info()
        db.close()
        
    if annotate_compatible:
        
        print "revise annotate_compatible"
        return
        
        parameters = {  'Db_name'           : DBNAME,
                        'Restriction'       : RESTRICTION,
                        'PropertyName'      : propname,
                        'UpdateStrategy'    : UPDATE,
                        'TemporalLogic'     : 'CTL',
                        'Description'       : propname,
                        'Formula'           : spec,
                        'InitialStates'     : init,
                        'VerificationType'  : 'forsome',
                        'Fix'               : {}}

        

        Annotation.TemporalLogic.run( parameters )


    

        
    if analyse_classes:
        parameters = { 'Db_name'        : DBNAME,
                       'Properties'     : CLASSES,
                       'Restriction'    : RESTRICTION}
        if export_csv:
            parameters['FileName'] = FNAMECSV
            
        Analysis.Classes.run( parameters )

    if analyse_relationships:
        parameters = {'Db_name'     : DBNAME,
                      'Properties1' : RELATIONSHIPS1,
                      'Properties2' : RELATIONSHIPS2,
                      'Restriction' : RESTRICTION}
        Analysis.Relationships.run( parameters )

    if analyse_strictestlabel:
        parameters = {'Db_name'       : DBNAME,
                      'Interactions'  : [],
                      'Restriction'   : RESTRICTION}

        Analysis.StrictestEdgeLabels.run( parameters )

    if annotate_upfunctions:
        params = {'Db_name'       : DBNAME,
                  'Restriction'   : RESTRICTION,
                  'Components'    : [],
                  'ShowEquations' : True}
        Annotation.UpdateFunctions.run( params )

    if annotate_attractors:
        params = {  'Db_name'        : DBNAME,
                    'Restriction'    : RESTRICTION,
                    'PropertyName'   : 'Attractors',
                    'InitialStates'  : '',
                    }
        
        Annotation.Attractors.run( params )

    
    

if __name__=='__main__':
    run()
