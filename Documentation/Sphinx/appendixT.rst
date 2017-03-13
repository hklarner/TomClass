Appendix T: Technical Documentation
###################################

	**Contents of Appendix T: Technical Documentation**

	* :ref:`appendixT_session`
	* :ref:`appendixT_predicates`
	* :ref:`appendixT_parser`
	* :ref:`appendixT_cpsolver`
	* :ref:`appendixT_database`
	* :ref:`appendixT_nusmv`

.. _appendixT_session:

Core/Session.py
***************
.. module:: Session

.. class:: Component(name, index)

	:param name: The name of the component.
	:type name: String
	:param index: The index of name in the sorted list of component names.
	:type index: Integer

	Contains information about a component.

	.. attribute:: name

		:type: String

		The name used in the regulatory graph.

	.. attribute:: index
		
		:type: Integer

		The index of the component in the sorted list of names.

	.. attribute:: max

		:type: Integer

		The maximal activity level of the component.

	.. attribute:: targets

		:type: List of :class:`components<Component>`
		The targets of the component in the regulatory graph.

	.. attribute:: regulators

		:type: List of :class:`components<Component>`

		The regulators of the component in the regulatory graph.

	.. attribute:: thresholds_to

		:type: Dictionary: (String, Tuple of Integers)

		Dictionary with target names as keys and integer thresholds as values.

	.. attribute:: thresholds_from

		:type: Dictionary: (String, Tuple of Integers)

		Dictionary with regulator names as keys and integer thresholds as values.

.. class:: Context

	Contains information about a regulatory context of a component.

	.. attribute:: index

		:type: Integer
	
		

.. class:: Messenger

	Prints messages to the screen. Available methods are:
	
	.. method:: error(Text)

	.. method:: warning(Text)

	.. method:: log(Text)

	.. method:: out(Text)

.. py:class:: Model

	.. attribute:: components_list

	.. attribute:: components_dict

	.. attribute:: contexts_list

	.. attribute:: contexts_dict

.. _appendixT_predicates:

Core/CPLanguage.py
******************
.. module:: CPLanguage

.. class:: Converter(Messenger, Model)

	:param Messenger: A :class:`Session.Messenger` object.
	:param Model: A :class:`Session.Model` object.

	The following method computes all parameter indeces that are referenced by a state formula and a component.

	.. method:: parameter_reference(StateFormula, Component)

		:return: ...
		:rtype: ...

	The following 8 methods convert :doc:`predicates <appendixB>` expressions to low-level constraints.
	Most of them require the above method :meth:`parameter_reference` to do so.
	The parameters and parameter types that the predicate methods share, are listed below.

	*Predicate parameters*

	:param Component: The component used for :ref:`parameter reference <appendixB_parameter_reference>`.
	:param StateFormula: A :ref:`state formula<appendixA_state_formulas>`.
	:type Component: String
	:type StateFormula: String
	:param Operator: One of ``'<','<=','=','>=','>','!='``.
	:type Operator: String
	:param Activity: An activity.
	:type Activity: Integer
	:param Quantifier: One of ``'All','Some'``
	:type Quantifier: String
	:param Label: One of ``'Activating','ActivatingOnly','Inhibiting','InhibitingOnly','Observable'``
	:type Label: String
	:param Threshold: The interaction threshold of the label.
	:type Thresholds: Integer
	:param Graph: A successor-based representation of a subgraph of the :ref:`unitary and asynchronous state transition graph<appendixA_async_dynamics>`. Each key of the dictionary is a state. The value of a key is a list of successor states.
	:type Graph: Dictionary
	:param Path: A list of states, representing a path in the :ref:`unitary and asynchronous state transition graph<appendixA_async_dynamics>`.
	:type Path: List of states

	.. method:: inequality_abs(Quantifier, StateFormula, Component, Operator, Activity)
		
		For semantics see :ref:`appendixB_inequalities`.

	.. method:: inequality_rel(Quantifier, StateFormula1, Component1, Operator, StateFormula2, Component2)

		For semantics see :ref:`appendixB_inequalities`.

	.. method:: identity(Quantifier, StateFormula, Component, Operator, Activity)

		For semantics see :ref:`appendixB_identities`.

	.. method:: multiplex(StateFormulas, Component)

		The "compounds" of a :ref:`multiplex <appendixB_multiplexes>`.
		The component that is regulated by the multiplex.
		For semantics see :ref:`appendixB_multiplexes`.

	.. method:: edge_label(Label, Regulator, Target, Thresholds, StateFormula="True")

		The optional :ref:`state formula<appendixA_state_formulas>` that restricts the contexts must satisfy the constraint (see :ref:`edge_label predicate<appendixB_edge_labels>`). The default ``True`` enforces no restriction.
		The regulator component of the interaction.
		The target component of the interaction.
		For semantics see :ref:`appendixB_edge_labels`.

	.. method:: subgraph(Graph)

		For semantics see :ref:`appendixB_subgraphs`.

	.. method:: path(Path)

		For semantics see :ref:`appendixB_subgraphs`.

	.. method:: compare(Quantifier, StateFormula, Component, Operator)

		For semantics see :ref:`appendixB_comparisons`.

.. _appendixT_parser:

Core/Parser.py
**************
.. module:: Parser

.. class:: Interactions(Messenger, FileName)

	:param Messenger: A :py:class:`Session.Messenger` object.
	:param FileName: Absolute path to interactions text file.
	:type FileName: String

	.. method:: success

		:return: Whether parsing was successful.
		:rtype: Boolean

	.. method:: parsed_interactions

		:return: The regulatory graph.
		:rtype: Dictionary

.. class:: Constraints(Messenger, FileName)

	:param Messenger: The :py:class:`Session.Messenger` object.
	:param FileName: Absolute path to interactions text file.
	:type FileName: String

	.. method:: success

		:return: Whether parsing was successful.
		:rtype: Boolean

	.. method:: parsed_constraints_niemeyer

		:return: The low-level parameter constraints in Python syntax.
		:rtype: String

	.. method:: parsed_constraints_minizinc

		:return: The low-level parameter constraints in MiniZinc syntax.
		:rtype: String


.. _appendixT_cpsolver:

Core/CPSolver.py
****************
.. module:: CPSolver

.. class:: Niemeyer(Messenger, Model, Constraints)

	:param Messenger: The :class:`Messenger<Session.Messenger>` object.
	:param Model: The :class:`Model<Session.Model>` object.
	:param Constraints: The :meth:`constraints<Parser.Constraints.parsed_constraints_niemeyer>` in Niemeyer format.
	:type Constraints: String

	.. method:: has_solutions

		:return: Whether the constraints are satisfiable.
		:rtype: Boolean
	
	.. method:: next
	
		:return: A feasible parametrization or "None" if there are no more.
		:rtype: List of Integers

.. _appendixT_database:

Core/Database.py
****************
.. class:: SQLite(Messenger, Model, 

.. _appendixT_nusmv:

Classifier/NuSMV.py
*******************
		
User Interfaces
***************
**new_project.py**::

	project_name = None
	regulatory_graph = None
	initial_constraints = None

**continue_project.py**::

	project_name = None
	classifier = None
	selection = "all"
	limit = None

**preferences.py**::
	
	minizinc_path = None
	nusmv_path = None


Property Specification Files
****************************
**Model Checking**::

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


