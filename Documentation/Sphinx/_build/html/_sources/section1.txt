Section 1: Initial Parametrizations
###################################
A new project is always created by running the script ``new_project.py``. The script requires a :literal:`project-name` and two input files: a :ref:`regulatory graph file<section1_file1>` and a :ref:`initial constraints file<section1_file2>`.
The :literal:`project-name` and the input file names are specified in the header of the script ``new_project.py`` by editing the respective lines:

	**new_project.py**::

		project_name = None
		regulatory_graph = None
		initial_constraints = None


The script will first create a new folder, with the given project name, and move it inside the tools projects folder. For reference, a copy of the input files is also moved into the new project folder. Finally a log file, with name ``<project-name>_log.txt``, is created in which all performed tasks are recorded.
The constraints file is then translated to a *finite domain constraint programming problem* and passed to the CP solver `MiniZinc <http://www.google.com/search?q=minizinc>`_. The solver will enumerate *all solutions*, i.e., all :ref:`parametrizations<appendixA_parametrizations>`, that satisfy the initial constraints and store them in a `sqlite3 database <http://www.google.com/search?q=sqlite3+python>`_ with the name ``<project-name>.db``. To call MiniZinc, the path to its executable must be specified in the file ``preferences.py`` by replacing ``None`` with the path string:

	**preferences.py**::

		minizinc_path = None

In the next sections we explain how regulatory graphs and initial constraints are specified in text files:

	**Contents of Section 1: Initial Parametrizations**

	* :ref:`section1_file1`
	* :ref:`section1_file2`

.. _section1_file1:

Input File 1: Regulatory graph
******************************
In :doc:`Appendix A<appendixA>` we defined a regulatory graph to consist of "anonymous" components :math:`v_1,v_2,\dots,v_n`.
In real applications we like to give names to the components. Hence, we define the token "name", that may be as short as one character, but must be alphanumeric and start with a letter:

	.. productionlist::
		name: `alpha`+ {`alpha` | `numeric`}
		alpha: A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W,X,Y,Z,a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z
		numeric: 0,1,2,3,4,5,6,7,8,9

A regulatory graph file is a text file that lists all interactions of the graph, *one per line*, followed by all thresholds of the interaction.
The regulator, target and thresholds must be seperated by a comma.

	**Regulatory graph file**

	.. productionlist::
		graph_file: `interaction`+
		interaction: `name` ',' `name` ',' `threshold` {',' `threshold`}
		threshold: 1,2,3,...

	:doc:`Running example <running_example>`: The regulatory graph file is:

	.. code-block:: none

		# Comments begin with a hash
		v1, v1, 1
		v1, v2, 1, 2
		v2, v1, 1
		v2, v2, 2

.. _section1_file2:

Input File 2: Initial Constraints
*********************************
Like regulatory graphs, initial constraints are specified in a text file. An initial constraint is a Boolean expression over the predefined predicates of :doc:`appendixB`.

	**Initial constraints file**

	.. productionlist::
		constraints_file: `constraints`*
		constraints: `constraint` | `constraints` and `constraints` | `constraints` or `constraints` | not `constraints`
		constraint: `inequality_abs` | `inequality_rel` | `identity` | `multiplex` | `edge_label` | `subgraph` | `path`
		

	:doc:`Running example <running_example>`: 
	
	.. code-block:: none

		# Comments begin with a hash
		Observable(v1, v1, 1) and Observable(v1, v2, 1) and
		Observable(v1, v2, 2) and ActivatingOnly(v2, v1, 1) and
		Some(True[v1] = 0) and Some(True[v1] = 2) and
		Multiplex(v1>0 and v2>0,v1=0,v2=0: v2)



