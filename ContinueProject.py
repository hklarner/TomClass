import os

import RegulatoryGraphs
import Database.Sqlite3 as DATABASE
reload(RegulatoryGraphs)
reload(DATABASE)



def run():
    PROJECT_NAME = 'Boolean4'
    MODEL = RegulatoryGraphs.Boolean4()
    CLASSIFIER = 'Custom1'
    SELECTION = 'K_v1_101>0 and K_v3_00>0 and (K_v2_11=1 and K_v0_11=1 and K_v0_00=1)'


    print 'Loading Project', PROJECT_NAME, '..',
    project_dir = os.path.join('Projects',PROJECT_NAME)
    if not os.path.isdir(project_dir):
        print 'Project',project_dir,'does not exist. Use "NewProject.py"..',
        return
    print 'ok'

    print 'Loading Classifier', '..',
    ClassModule = __import__('Classifier.'+CLASSIFIER, fromlist=['Interface'])
    classifier = ClassModule.Interface(MODEL)
    print 'ok'

    database = DATABASE.Interface(PROJECT_NAME, MODEL)
    database.register_classifier(classifier)
    database.set_selection(SELECTION)
    

    print 'Starting classification..',
    while not database.is_finished():
        database.perform_classification()
    print 'done'

    database.clear_selection()
    database.close()
    

if __name__=='__main__':
    run()
    
