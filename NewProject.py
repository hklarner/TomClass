# -*- coding: utf-8 -*-

import constraint as CP
import itertools as IT
import os
import csv

import RegulatoryGraphs
import ConstraintLanguage.Enumerator as ENUMERATOR
import Database.Sqlite3 as DATABASE
reload(RegulatoryGraphs)
reload(ENUMERATOR)
reload(DATABASE)



def run():
    PROJECT_NAME = 'ABC'
    MODEL = RegulatoryGraphs.ABC()
    CONSTRAINT = 'Multiplex(A=1 and B=1, C=1 [C]) and (NotObservable(C,A,1) or ActivatingOnly(C,A,1)) and Activating(C,B,1) and NotInhibiting(C,B,2)'+\
                 'and Some(A>0 [C] = 0)'
    RegulatoryGraphs.PrintFullInfo(MODEL)

    project_dir = os.path.join('Projects',PROJECT_NAME)
    if os.path.isdir(project_dir):
        print 'Project', PROJECT_NAME, 'already exists. Use "ContinueProject.py".'
        #return
    else:
        print 'Creating directory',project_dir,'..',
        os.mkdir(project_dir)
        print 'ok'

    writer = DATABASE.Interface(PROJECT_NAME, MODEL)
    for sol in ENUMERATOR.Parametrizations(MODEL, CONSTRAINT):
        writer.insert_parametrization(sol)
    writer.close()

if __name__=='__main__':
    run()

