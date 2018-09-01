

import sys
import itertools as IT
import random as RND

import Instantiation
import Annotation
import Analysis
from Engine import Database
from Engine import ModelChecking as MCheck
import time




DBNAME = 'example1.sqlite'
FNAMECSV = 'example1.csv'

create                  = 1

annotate_compatible     = 1




analyse_classes         = 1
export_csv              = 1
analyse_relationships   = 1
analyse_strictestlabel  = 1

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
        parameters = {  'Db_name'           : DBNAME,
                        'Restriction'       : RESTRICTION,
                        'Property_name'     : "ALL_ACTIVE",
                        'Description'       : "Exists a path a state 111",
                        'Formula'           : "EF(v1 & v2 & v3)",
                        'Initial_states'    : "TRUE",
                        'Verification_type' : 'forsome',
                        'Fix'               : {}}



        Annotation.CTL.run( parameters )





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




if __name__=='__main__':
    run()
