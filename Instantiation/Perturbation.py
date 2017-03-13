
import os
import itertools

from Engine import Models
from Engine import Database
from Engine.Constraints import Parser
from Engine.Constraints import NiemeyerSolver


keywords = {'Db_name'               : 'ABC.sqlite',
            'Perturbation_depth'    : 2}

def run( Parameters, verbose=-1 ):

    print "unstable, revise"
    raise Exception
    
    for key in Parameters:
        if not key in keywords:
            print ' ** Unknown parameter: "%s"'%key
            print '    Parameters must belong to:',','.join(keywords)
            raise Exception


    Db_name      = Parameters['Db_name']
    Components   = Parameters['Components']
    Interactions = Parameters['Interactions']
    Constraint   = Parameters['Constraint']


    Model = Models.Interface(Components, Interactions)
    if verbose>-1: Model.info()
    if os.path.isfile(Db_name):
        if 1:
            os.remove(Db_name)
            Database.New(Db_name, Model)
    else:
        Database.New(Db_name, Model)

    cps = Parser.Interface(Model)
    cps.parse(Constraint)
    
    db = Database.Instantiation(Db_name)
    db.newProperty(Property_name, 'int')

    roots = 0
    for params in cps.solutions():
        roots+=1
        db.insert(params, {Property_name:0})
        
        for depth in range(1,Perturbation_depth+1):

            for perturbed in itertools.combinations(Model.parameters, depth):
                options = []
                
                for p in perturbed:
                    options.append([i for i in p.range if abs(i-params[p])==1])
            
                for choice in itertools.product(*options):
                    items = zip(perturbed,choice)
                    new_params = dict(params.items()+items)

                    db.insert(new_params, {Property_name:depth})
    db.close()

    db = Database.Analysis(Db_name)
    size = db.size-roots
    db.close()
    if verbose>-1: 
        print
        print '---Perturbations of a pool defined by CP'
        print 'Created database:            ',"'"+Db_name+"'"
        print 'Perturbation depth:          ',Perturbation_depth
        print 'Perturbation name in DB:     ',"'"+Property_name+"'"
        print 'Constraint:                  ',"'"+Constraint+"'"
        print 'Initial parametrizations:    ',roots
        print 'Perturbed parametrizations:  ',size
    

    

if __name__=='__main__':
    run()
