Section 2: Classifying
######################
Classifying is the process of specifying an algorithm, called *classifier*, that computes a value, called *class label*, for a given parametrization. The labels are added to the existing database in a column with a user-defined title, called *property name*. The central part of classifying is a loop over a user-defined selection of parametrizations. In each iteration the current parametrization is passed to the classifier. The class label it returns is stored and the next parametrization is handed to the classifier.

	*Example*: Suppose that the parametrizations of a project have previously been classified by the number of fixpoints in their asynchronous transition graphs. The project database therefore contains a column entitled :literal:`Fixpoints` with integer values. In a second step, all parametrizations with exactly one fixpoint shall be divided into the class that reproduces a time series called ``TS1``, and the class that does not. The specification for time series ``TS1`` together with the selection ``Fixpoints=1`` is passed to the *time series classifier*, which computes Boolean labels for the porperty ``TS1`` in the *classification loop* over all parametrizations in the selection.

.. image:: images/section2_01.jpg
	:scale: 70%
	:align: center


To continue work on an existing project, i.e., to classify a selection of models by a given property specification, the script :literal:`continue_project.py` is called. The script requires the *project-name* of the project to be continued, the *classifier* that is to be used, a *selection* of parametrizations that is to be classified and possibly a *limit* that sets the maximum number of calls of the classifier. These four inputs are specified by editing the header of the file :literal:`continue_project.py`:

	**continue_project.py**::

		project_name = None
		classifier = None
		selection = "all"
		limit = None

The script first confirms, that a project :literal:`Projects/<project_name>` exists and that it contains a model database :literal:`<project_name>.db`.

*Input 1: classifier*: The variable ``classifier`` must either be assigned to the name of a *property file*, or the name of a *custom classifier*. A property file is a text file that contains a property description for one of the three classifiers that are delivered with the tool: :ref:`model checking <section2_type1>`, :ref:`trap set search<section2_type2>`, :ref:`time series existence <section2_type3>`. A custom classifier is a Python script that computes class labels for models. Its property description is hard-wired into it by the author of the script. A detailed description of the interface between :literal:`continue_project.py` and custom classifiers is given in :ref:`Section: Custom Classifier <section2_custom_classifier>`.

*Input 2: selection*: The variable ``selection`` defines which parametrizations ought to be classified in this run. It is a Boolean expression over the :ref:`predicates <appendixA_state_formulas>` of :doc:`appendixB`, but also includes SQL statements over class labels already attached to the parametrizations:

	**Selections**

	.. productionlist::
		selection: `selection_atom` | 'not' `selection` | `selection` 'and' `selection` | `selection` 'or' `selection`
		selection_atom: `constraint` | `property`
		property: hmm

If the value of ``selection`` is ``None``, then *all* parametrizations without a label will be classified.
 
*Input 3: limit*: The variable ``limit`` is either set to ``None``, in which case the classification loop will continue until all parametrizations are labeled, or if an integer is assigned to it, the loop stops after ``limit`` iterations.

In the next sections we will discuss:

	**Contents of Section 2**

	* :ref:`section2_type1`
	* :ref:`section2_type2`
	* :ref:`section2_type3`
	* :ref:`section2_custom_classifier`

.. _section2_type1:

Model Checking
**************
Any state transition graph, whether *synchronous*, *asynchronous*, *unitary* or *non-unitary*, can naturally be interpreted as a *transition system for model checking*. Recall :ref:`Appendix A: Asynchronous dynamics <appendixA_async_dynamics>` for definitions of the state transition graph, and [Bernot04]_ for a discussion of model checking in the context of regulatory networks.
A *model checking specification file* is a text file, that contains a *formula*: either a *linear time logic* formula, i.e., LTL, or a *computational tree logic* formula, i.e., CTL, a description of the *initial states* in form of a :ref:`subset term <appendixA_state_formulas>`, the *search type*, a *property name*, a *property description* and two values specifying the type of dynamics to be considered.

The *model checking classifier* divides parametrizations into two classes: those whose dynamics satisfy the specification, denoted by the class label ``True`` and those whose dynamics do not satisfy the specification, denoted by class label ``False``. The dynamics of a parametrization satisfies a specification if there is a state among the initial states (search type ``exists``), or all initial states (search type ``forall``), satisfy the temporal formula. A formula may be either a LTL or CTL formula. Both languages and conditions under which a state satisfy a formula are discussed in, e.g., [Baier08]_.

We use the `NuSMV v2.5 <http://nusmv.fbk.eu/NuSMV/>`_ symbolic model checking software to decide whether the formula holds. The path to the NuSMV executable must be specified in the text file :literal:`preferences.py` by replacing :literal:`None` with the path string:

	**preferences.py**::

		nusmv_path = None

	**Model checking specification file**

	.. productionlist::
		model_checking_file: `model_line` `name_line` `desc_line` `unit_line` `sync_line` `init_line` `search_line` `spec_line` 
		model_line: 'classifier = nusmv model checking'
		name_line: 'property_name =' `name`
		desc_line: 'property_description =' `description`
		unit_line: 'unitary =' `bool`
		sync_line: 'synchronous =' `bool`
		init_line: 'initial_states =' `selection`
		search_line: 'search = ' ('exists' | 'forall')
		spec_line: ('ctl' | 'ltl') '_spec =' `temporal logic formula`
		bool: 'true' | 'false'
		description: {`name` | ' '}



Example of a model checking specification file:
	.. code-block:: none

		# Comments begin with a hash
		classifier = nusmv model checking
		property_name = RpoS
		property_description = Is the entry into stationary phase always preceded by the accumulation of the stress response regulator RpoS?

		unitary = true
		synchronous = false
		initial_states = v1=0 and (v2>0 or v3=2)
		ctl_spec = EF(Xrrn=0) & !E(Xrpos>0 U Xrrn=0)


.. _section2_type2:

Trap Set Search
***************
Often, we want to divide the parametrizations of a regulatory network into two classes: the one whose dynamics stabilizes within a rectangular region of state space, denoted by class label ``True``, and the one whose dynamics does not stabilize in that region, denoted by class label ``False``. The *trap set search* classifier performs this task: it decides for a given rectangular region and parametrization, whether the transition graph contains a *trap set* in the region or not. Recall, that a subset :math:`Y\subset X` of states of a transition graph :math:`(X,T)` is called trap set, if :math:`\forall y\in Y:\; yx\in T\implies x\in Y`. A rectangular region, or *box* for short, is defined by a function :math:`B:V\rightarrow \{[a..b] \;|\; a\leq b\in\mathbb{N}\}` such that :math:`B(v_i)\subseteq [0..\rho(v_i)]`, where :math:`\rho(v_i)` is the maximal activity of :math:`v_i` (see :ref:`Appendix A: Regulatory graph <appendixA_reg_graphs>` for definitions). The interval :math:`B(v_i)=[a..b]` is called *box interval*. A transition graph belongs to the stabilizing class, if there is a trap set :math:`Y\subseteq X`, such that :math:`Y\subseteq \prod_{i=1}^n B(v_i)` is inside the box.

A trap set specification file is a text file that specifies the box intervals of each component. If the *box interval* of a component is equal to its activity range, the interval may be omitted.


	**Trap set specification file**

	.. productionlist::
		trap_set_file: `trap_line` `name_line` `desc_line` `box_line`
		trap_line: 'classifier = trap set'
		name_line: 'property_name =' `name`
		desc_line: 'property_description =' `description`
		box_line: `interval` {',' `interval`}
		interval: `name` '[' `integer` [',' `integer`] ']'


Example of trap set specification file:
	.. code-block:: none

		# Comments begin with a hash
		classifier = trapset
		property_name = t1
		property_description = Is there a trap set with Xyrn=0, Xrrn>0 and Xppn>1?

		box = Xrrn[1,2], Xryn[0,1], Xccn[2], Xyrn[0], Xppn[2,3]

.. _section2_type3:

Time series
***********


	**Time series specification file**

	.. productionlist::
		time_series_file: `time_line` `name_line` `desc_line` `measurement_line` `measurement_line`+
		time_line: 'classifier = time series'
		name_line: 'property_name =' `name`
		desc_line: 'property_description =' `description`
		measurement_line: `measurement` {' ' `measurement`}
		measurement: `mon_measurement` | `not_mon_measurement`
		mon_measurement: `name` '[' `integer` ']'
		not_mon_measurement: `name` '(' `integer` ')'

Example of a time series specification file:
	.. code-block:: none

		classifier = time series
		property_name = timeseries1
		property_description = Is the time series reproduced?

		Xrrn[1] Xryn(0) Xccn[2] Xyrn[0] Xppn(2)
		Xrrn[1] Xryn(0) Xccn(2) Xyrn[0] Xppn(3)
		Xrrn[0] Xryn(0) Xccn[1] Xyrn[0] Xppn(2)

.. _section2_custom_classifier:

Custom Classifier Interface
***************************
A custom classifier is an implementation of an algorithm in Python, that computes *class labels* for parametrizations.
It is a *class* that contains information about the property that is investigated, i.e., a short name stored in :py:attr:`Classifier.property_name`, that is used as a column title in the database, the data type of the property stored in :py:attr:`Classifier.data_type` and a text description of the property stored in :py:attr:`Classifier.property_description`.
The classifier is instantiated and passed to ``continue_project.py`` where its *interface methods* are called repetitively during the *classification loop*. We discuss the interface methods in detail below.

For convenience, a Python object called :py:obj:`Model` is passed to the classifier on instatiation. A model has a number of methods that facilitate querying the current parametrization for target values and transitions. It also contains data to obtain information about the associated regulatory graph. Once every iteration, the classification loop will update the model by replacing the old with the current parametrization, and call the first interface method, :py:meth:`compute_label`, of the custom classifier. This method must return the label for the current parametrization. If the classifier computed *constraints* that are *sufficient* to imply certain class labels, it should return them via the second interface mathod, :py:meth:`Classifier.sufficient_constraints`, in form of a list of tuples consisting of (*constraint*, *label*). For every tuple, all unlabeled parametrizations that satisfy the *constraint* will be assigned the *label* - without being explicitly passed to the classifier. This may speed up classifying, because many parametrizations may be labeled at once. Finally, ``continue_project.py`` calls :py:meth:`Classifier.priorities`, the third interface method, to inquire a constraint that the next unclassified paramatrization should satisfy. ``continue_project.py`` will then attempt to find an unlabeled parametrization that satisfies this priority constraint.

.. image:: images/section2_02.jpg
	:scale: 70%
	:align: center

Property Specifications
-----------------------

	.. py:attribute:: Classifier.property_name

		(String) A short name that is used as a column header in the parametrization database.

	.. py:attribute:: Classifier.property_description

		(String) A text describtion of the property.

	.. py:attribute:: Classifier.data_type

		(String) A description of the data type of the class labels. Allowed types are ``'string'``, ``'integer'`` and ``'boolean'``.

The Loop Interface
------------------
	.. py:method:: Classifier.compute_label

		:return: The label for the current parametrization.
		:rtype: String


	.. py:method:: Classifier.sufficient_constraints

		:return: Sufficient constraints and labels that are used to do *bulk labeling*. All non-classified parametrizations, that satisfy one of the constraints will be assigned the corresponding label.
		:rtype: List of tuples

		Each tuple in the return list consists of a constraint string and a label string.
		If no sufficient constraints could be obtained, an empty list should be returned.

	.. py:method:: Classifier.priorities

		:return: A constraint that describes parametrizations that are preferred in the next classification iteration.
		:rtype: String

		If the classifier has no priority, an empty string should be returned.


Inquiries about the Regulatory graph
------------------------------------

	The :py:class:`Model` class provides several attributes for inquiring the regulatory graph of the project.


	.. py:attribute:: Model.components

		(Tuple of strings) Sorted tuple of the component names.

		:doc:`Running example <running_example>`::

			Model.components
			>>> ('v1','v2')

	.. py:attribute:: Model.regulators

		(Dictionary) Components are keys and sorted tuple of regulators are values.

		:doc:`Running example <running_example>`::

			Model.regulators
			>>> {'v1':('v1','v2'), 'v2':('v1','v2')}

	.. py:attribute:: Model.targets

		(Dictionary) Components are keys and sorted tuple of targets are values.

		:doc:`Running example <running_example>`::

			Model.targets
			>>> {'v1':('v1','v2'), 'v2':('v1','v2')}

	.. py:attribute:: Model.thresholds

		(Dictionary) Interactions are keys and sorted tuple of thresholds are values.
		Interactions are tuples consisting of components.

		:doc:`Running example <running_example>`::

			Model.thresholds
			>>> {('v1', 'v2'): (1, 2), ('v1', 'v1'): (1,), ('v2', 'v1'): (1,), ('v2', 'v2'): (2,)}

	.. py:attribute:: Model.maxactivity

		(Dictionary) Components are keys and maximal activities are values.

		:doc:`Running example <running_example>`::

			Model.maxactivity
			>>> {'v1': 2, 'v2': 2}

Inquiries about the Current Parametrization
-------------------------------------------

Description of methods for inquiring the transition graph of the current parametrization. Examples are given for the :doc:`running example <running_example>`.

	.. py:method:: Model.asynchronous_successors(State)

		:param State: Contains one integer for each component of the :ref:`regulatory graph<appendixA_reg_graphs>`. The :math:`i^{th}` integer represents the activity of the component that is at the :math:`i^{th}` position in the sorted list of component names.
		:type State: List of integers
		:return: A list of successor states of the :ref:`asynchronous and unitary state transition graph<appendixA_async_dynamics>` of the current parametrization.
		:rtype: List of States.

	.. py:method:: Model.synchronous_successor(State)

		:param State: Contains one integer for each component of the :ref:`regulatory graph<appendixA_reg_graphs>`. The :math:`i^{th}` integer represents the activity of the component that is at the :math:`i^{th}` position in the sorted list of component names.
		:type State: List of integers
		:return: The successor state of the :ref:`synchronous and unitary state transition graph<appendixA_async_dynamics>` of the current parametrization.
		:rtype: A State.

	.. py:method:: Model.update_Function(State)

		:param State: Contains one integer for each component of the :ref:`regulatory graph<appendixA_reg_graphs>`. The :math:`i^{th}` integer represents the activity of the component that is at the :math:`i^{th}` position in the sorted list of component names.
		:type State: List of integers
		:return: The successor state of the :ref:`synchronous and non-unitary state transition graph<appendixA_async_dynamics>` of the current parametrization.
		:rtype: A State.

	.. py:method:: Model.target_values(StateFormula, Component)

		:param StateFormula: A :ref:`state formula<appendixA_state_formulas>`.
		:type StateFormula: String
		:param Component: The component used for :ref:`parameter reference <appendixB_parameter_reference>`.
		:type Component: String
		:return: Target values of the referenced parameters of current parametrization .
		:rtype: List of integers

	.. py:method:: Model.inequality_abs(StateFormula, Component, Operator, Activity)

		:param StateFormula: A :ref:`state formula<appendixA_state_formulas>`.
		:type StateFormula: String
		:param Component: The component used for :ref:`parameter reference <appendixB_parameter_reference>`.
		:type Component: String
		:param Operator: One of ``'<','<=','=','>=','>','!='``.
		:type Operator: String
		:param Activity: An activity.
		:type Activity: Integer
		:return: Whether the current parametrization satisfies the :ref:`inequality_abs predicate<appendixB_inequalities>` with the given arguments.
		:rtype: Boolean


	.. py:method:: Model.inequality_rel(StateFormula1, Component1, Operator, StateFormula2, Component2)

		:param StateFormula1: The left-hand side :ref:`state formula<appendixA_state_formulas>`.
		:type StateFormula1: String
		:param Component1: The component for left-hand side :ref:`parameter reference <appendixB_parameter_reference>`.
		:type Component1: String
		:param Operator: One of ``'<','<=','=','>=','>','!='``.
		:type Operator: String
		:param StateFormula2: The right-hand side :ref:`state formula<appendixA_state_formulas>`.
		:type StateFormula2: String
		:param Component2: The component for right-hand side :ref:`parameter reference <appendixB_parameter_reference>`.
		:type Component2: String
		:return: Whether the current parametrization satisfies the :ref:`inequality_rel predicate<appendixB_inequalities>` with the given arguments.
		:rtype: Boolean

	.. py:method:: Model.identity(Quantifier, StateFormula, Component, Operator, Activity)

		:param Quantifier: One of ``'All','Some'``
		:type Quantifier: String
		:param StateFormula: A :ref:`state formula<appendixA_state_formulas>`.
		:type StateFormula: String
		:param Component: The component used for :ref:`parameter reference <appendixB_parameter_reference>`.
		:type Component: String
		:param Operator: One of ``'<','<=','=','>=','>','!='``.
		:type Operator: String
		:param Activity: An activity.
		:type Activity: Integer
		:return: Whether the current parametrization satisfies the :ref:`inequality_abs predicate<appendixB_inequalities>` with the given arguments.
		:rtype: Boolean

	.. py:method:: Model.multiplex(StateFormulas, Component)

		:param StateFormulas: The "compounds" of a :ref:`multiplex <appendixB_multiplexes>`.
		:type StateFormulas: List of strings
		:param Component: The component that is regulated by the multiplex.
		:type Component: String
		:return: Whether the current parametrization satisfies the :ref:`multiplex predicate<appendixB_multiplexes>` with the given arguments.
		:rtype: Boolean

	.. py:method:: Model.edge_label(Label, Regulator, Target, Thresholds, StateFormula="True")

		:param Label: One of ``'Activating','ActivatingOnly','Inhibiting','InhibitingOnly','Observable'``
		:type Label: String
		:param Threshold: The interaction threshold of the label.
		:type Thresholds: Integer
		:param StateFormula: The optional :ref:`state formula<appendixA_state_formulas>` that restricts the contexts must satisfy the constraint (see :ref:`edge_label predicate<appendixB_edge_labels>`). The default ``True`` enforces no restriction.
		:type StateFormula: String
		:param Regulator: The regulator component of the interaction.
		:type Regulator: String
		:param Target: The target component of the interaction.
		:type Target: String
		:return: Whether the current parametrization satisfies the :ref:`edge_label predicate<appendixB_edge_labels>` with the given arguments.
		:rtype: Boolean

	.. py:method:: Model.subgraph(Graph)

		:param Graph: A successor-based representation of a subgraph of the :ref:`unitary and asynchronous state transition graph<appendixA_async_dynamics>`. Each key of the dictionary is a state. The value of a key is a list of successor states.
		:type Graph: Dictionary
		:return: Whether the current parametrization satisfies the :ref:`subgraph predicate<appendixB_subgraphs>` with the given argument.
		:rtype: Boolean

	.. py:method:: Model.path(Path)

		:param Path: A list of states, representing a path in the :ref:`unitary and asynchronous state transition graph<appendixA_async_dynamics>`.
		:type Path: List of states
		:return: Whether the current parametrization satisfies the :ref:`path predicate<appendixB_subgraphs>` with the given argument.
		:rtype: Boolean

	.. py:method:: Model.compare(Quantifier, StateFormula, Component, Operator)

		:param StateFormula: A :ref:`state formula<appendixA_state_formulas>`.
		:type StateFormula: String
		:param Quantifier: One of ``'All','Some'``
		:type Quantifier: String
		:param Component: The component used for :ref:`parameter reference <appendixB_parameter_reference>`.
		:type Component: String
		:param Operator: One of ``'<','<=','=','>=','>','!='``.
		:type Operator: String
		:return: ...
		:rtype: ...




Custom Classifier Implementation Examples
*****************************************

Deterministic path classifier
-----------------------------

As an example we will implement an algorithm that computes the length of a *deterministic path* starting in a given initial state.
A path :math:`(x^1,x^2,\dots,x^{k+1})` of the asynchronous transition graph :math:`(X,T)` is *deterministic*,
if for all :math:`i\in[1..k],z\in X:\;x^iz\in T\implies z=x^{i+1}`. The length of such a path is :math:`k`.
As we will see, this classifier serves as a good example for how custom algorithms are implemented, because it is simple, and makes use of most features of the interface.
We create a file called ``detpath.py`` which contains a single class called ``Classifier``.
During initialization the :py:class:`Model` is stored as an attribute, and the initial state is computed, depending on the number of components of the network. This is an example of *hard-wiring* the property information that the predefined classifiers get from text files (see :ref:`Type 1 <section2_type1>`, :ref:`Type 2 <section2_type2>` and :ref:`Type 3 <section2_type3>`) into the algorithm.
In this example the initial state is the one, where every component is below all its thresholds, i.e., the *zero* state.

	**detpath.py**::

		class Classifier(object):
			def __init__(self, Model):
				self.property_name = 'dpzero'
				self.property_description = 'Computes the length of a deterministic path starting in the zero state.'
				self.data_type = 'integer'
				self.model = Model
				self.initial_state = [0 for i in Model.components]




























