
A python environment for classifying discrete regulatory models.

Requires GUROBI for constraint satisfaction. If you don't have GUROBI installed insert comment out `import gurobipy` in file 

* TomClass/Engine/PrimeImplicants/LPSolver.py

If you use NuSMV model checking you must enter the path to the NuSMV executable in variable `NUSMV_CMD` in file

* TomClass/Engine/ModelChecking.py

