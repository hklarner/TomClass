Appendix B: Parameter Constraint Language
#########################################
In this section we introduce a high-level parameter constraint language. In :doc:`Section 1: Initial Parametrizations <section1>` we use this language to define the initial parametrizations.
In :doc:`Section 2: Classifying <section2>` the same language is used to mark parametrizations that ought to be classified, but also to speed up the classification by *learning* from the computations performed for a particular parametrization.
The language is based on an original approach to referencing parameters, and 6 types of predicates that use this approach.
We will discuss the semantics and possible applications in modelling of each of the 6 predicate types we have implemented.

	**Low-level constraints**

	We call constraints *low-level*, if they are logical propositions over parameter inequalities.
	A parametrization :math:`P` satisfies a low-level constraint :math:`\gamma`, if the :math:`P`-valuation, :math:`P(\gamma)`, of the constraint is true.

	:doc:`Running example <running_example>`: An example of a low-level constraint :math:`\gamma` is

	.. math::

		\gamma\equiv\quad(K_1^{00}>0\;and\; K_1^{01}>K_1^{10}).

	**P-valuation**

	A parametrization :math:`P` satisfies the low level constraint :math:`\gamma`, if

	.. math::

		P(\gamma):\equiv\quad(P_1^{00}>0\;and\; P_1^{01}>P_1^{10})=True.

.. long version
	
	\;or\;(K_1^{10}=K_1^{11}\;and\;K_2^{00}>K_1^{01})
	\;or\;(P_1^{10}=P_1^{11}\;and\;P_2^{00}>P_1^{01})

The difficulty here is that biological assumptions are in general not precise enough to be formulated as short low-level constraints.
Rather, the biological assumptions are characterized by ambiguity, which results in long low-level constraints, that are tedious to assemble by hand.

A good example of this vagueness are assumptions about the effect that a regulator has on its target, i.e., the *edge label* of an interaction. We may know that a regulator inhibits the activity of its target, but we do not know the exact context in which the inhibition is observable. We can only safely assume that *there is* a context such that increasing the regulator's activity decreases the target's activity.

	*Example*: Consider a regulatory graph, where a component :math:`v_1` has exactly 3 regulators :math:`v_2,v_3` and :math:`v_4`.
	Assume also that each interaction targeting :math:`v_1` has exactly 2 :ref:`intensities <appendixA_interaction_intensities>`.
	We want make the assumption that :math:`v_2` is an inhibitor of the activity of :math:`v_1`, but we do not know which context is supposed to demonstrate the inhibition. We must consider all possible cases feasible and resort to the following low-level constraint:

	.. math::

		K_1^{000}>K_1^{100}\;or\;K_1^{001}>K_1^{101}\;or\;K_1^{010}>K_1^{110}\;or\;K_1^{011}>K_1^{111}

For this reason we have devised *predicates*, like :math:`Inhibiting(v_2,v_1)`, that are equivalent to longer low-level constraints, but make the modelling process more convenient, because we do not need to think about *which* parameters are concerned nor *how* the respective inequalities are connected.

The predicates work by a feature called *parameter reference*.
It is a concise form of refering to a subset :math:`K'\subset K_{\mathcal R}` of the kinetic parameters of a regulatory graph :math:`\mathcal R`.
All that is required to define the set :math:`K'` is a state formula :math:`\phi` and a component :math:`v_i`:

.. beispiel

	To motivate the idea, consider the following case. Given a subset :math:`Y\subseteq X` of the :ref:`state space <appendixA_state_space>`, we want to construct the constraint: *There is* a state :math:`x\in Y`, such that the :ref:`target value` of component :math:`v_i` in :math:`x` is equal to :math:`0`. The regulatory graph and set :math:`Y` are sufficient to determine the relevant set of parameters :math:`\{K_{i}^{c_1},K_{i}^{c_2},\dots,K_{i}^{c_k}\}\subset K` that represent all contexts of :math:`v_i` in all states :math:`Y`. We can then construct the constraint:

	.. math::

		K_{i}^{c_1}=0\;or\;K_{i}^{c_2}=0\;or\;\dots\;or\;K_{i}^{c_k}=0.


	By parameter reference we mean determining parameters whose evaluated state formula intersects a set :math:`Y` that may of course also be given by a state formula.

.. _appendixB_parameter_reference:

	**Parameter reference**
	
	Recall from :ref:`Appendix A: Regulatory contexts <appendixA_regulatory_context>` that :math:`\psi_i^c` denotes the state formula associated to the regulatory context :math:`c` of component :math:`v_i`.
	The parameter reference, denoted by :math:`K_i[\phi]`, of a given state formula :math:`\phi` and a component :math:`v_i` is defined to be the set of all kinetic parameters whose context states :math:`X[\psi_i^c]` *intersect* :math:`X[\phi]`:

		.. math::
		
			K_i[\phi]:=\{K_i^c\in K\;|\; X[\phi]\cap X[\psi_i^c]\neq\emptyset\}
	
	In our constraint language, the syntax of a parameter reference is:

		.. productionlist::
			parameter_reference: `state_formula` '[' `component` ']'


	:doc:`Running example <running_example>`: Consider the state formula :math:`\phi:\equiv\quad v_1\leq v_2`. The referenced states, in concise tuple notation, are:

	.. math::

		X[\phi]=\{00,01,11,02,12,22\}

	With :math:`\phi` we can make a parameter reference for either :math:`v_1` or :math:`v_2`:

	.. math::

		K_1[\phi]=\{K_1^{00},K_1^{01},K_1^{11}\},\;\;K_2[\phi]=\{K_2^{00},K_2^{10},K_2^{01},K_2^{11},K_2^{21}\}

	The reaseon why :math:`K_1^{01}\in K_1[\phi]` is that :math:`X[\psi_1^{01}]=\{01,02\}`, which intersects :math:`X[\phi_1]`.
	The reason why :math:`K_1^{10}\notin K_1[\phi]` is that :math:`X[\psi_1^{10}]=\{10,20\}`, which does not intersect :math:`X[\phi_1]`.

Now we are set to discuss the following constraints:

	**Table of contents of Appendix B**

	* :ref:`appendixB_inequalities`
	* :ref:`appendixB_identities`
	* :ref:`appendixB_multiplexes`
	* :ref:`appendixB_edge_labels`
	* :ref:`appendixB_subgraphs`
	* :ref:`appendixB_comparisons`

.. _appendixB_inequalities:

Predicate Type 1: Inequalities
*******************************
Inequality constraints restrict the values of a set of parameters to satisfy all - or some - inequalities. The left-hand side of each inequality is always from the first set of parameters. For the right-hand side, we distinguish two types of inequalities: Either the right-hand side of the inequality is an integer value, in which case we have an :token:`inequality_abs` constraint, or a second set of parameters is passed to the right hand side, in which we have a :token:`inequality_rel` constraint. 

	**Syntax**

	.. productionlist::
		inequality: `inequality_abs` | `inequality_rel`
		inequality_abs: `quantifier` '(' `parameter_reference` `operator` `activity` ')'
		inequality_rel: `quantifier` '(' `parameter_reference` `operator` `parameter_reference` ')'
		operator: '<'|'<='|'='|'>='|'>'|'!='

	**Semantics**

	*Inequality_Abs*: Let :math:`K'=\{K_i^{c_1},K_i^{c_2},\dots,K_i^{c_r}\}` be the referenced parameters, :math:`\star\in\{<,\leq,=,\geq,>,\neq\}` the operator and :math:`a\in\mathbb N` the activity of an :token:`inequality_abs` constraint.
	Depending on the quantifier, the low-level constraint becomes:

	.. math::
		\begin{array}{ll}
		\textrm{Quantifier}&	\textrm{Low-level constraint}\\
		\hline\hline
		\textrm{All}:&			K_i^{c_1}\star a\;and\;K_i^{c_2}\star a\;and\;\dots\;and\; K_i^{c_r}\star a\\
		\textrm{Some}:&			K_i^{c_1}\star a\;or\;K_i^{c_2}\star a\;or\;\dots\;or\; K_i^{c_r}\star a
		\end{array}

	*Inequality_Rel*: Let :math:`K'=\{K_i^{c_1},K_i^{c_2},\dots,K_i^{c_r}\}` be the first referenced parameters, :math:`\star\in\{<,\leq,=,\geq,>,\neq\}` the operator and :math:`K''=\{K_j^{d_1},K_j^{d_2},\dots,K_j^{d_s}\}` the second referenced parameters of an :token:`inequality_rel` constraint.
	Depending on the quantifier, the low-level constraint becomes:

	.. math::
		\begin{array}{ll}
		\textrm{Quantifier}&	\textrm{Low-level constraint}\\
		\hline\hline
		\textrm{All}:&			K_i^{c_1}\star K_j^{d_1}\;and\;\dots\;and\;K_i^{c_r}\star K_j^{d_1}\;and\;\dots\;and\;K_i^{c_1}\star K_j^{d_s}\;and\;\dots\;and\;K_i^{c_r}\star K_j^{d_s}\\
		\textrm{Some}:&			K_i^{c_1}\star K_j^{d_1}\;or\;\dots\;or\;K_i^{c_r}\star K_j^{d_1}\;or\;\dots\;or\;K_i^{c_1}\star K_j^{d_s}\;or\;\dots\;or\;K_i^{c_r}\star K_j^{d_s}
		\end{array}

	:doc:`Running example <running_example>`: Let us consider the state formula :math:`v_1\leq v_2`. The parameter reference for :math:`v_1` is: :math:`K_1[v_1\leq v_2]=\{K_1^{00}, K_1^{01}, K_1^{11}\}`,
	and the one for :math:`v_2` is :math:`K_2[v_1\leq v_2]=\{K_2^{00},K_2^{10},K_2^{01},K_2^{11},K_2^{21}\}`. With the two quantifiers we can formulate two :token:`inequality_abs` constraints and two :token:`inequality_rel` constraints. Their equivalent low-level constraints are:

		.. math::
			\begin{array}{ll}
			{\tt Some(v1<=v2[v1] = 0)}\equiv\quad& K_1^{00}=0\;or\;K_1^{01}=0\;or\;K_1^{11}\\
			{\tt All(v1<=v2[v1] = 0)}\equiv\quad& K_1^{00}=0\;and\;K_1^{01}=0\;and\;K_1^{11}\\
			{\tt Some(v1<=v2[v1] < v1<=v2[v2])}\equiv\quad&   K_1^{00}<K_2^{00}\;or\;K_1^{01}<K_2^{00}\;or\;K_1^{11}<K_2^{00}\;or\;\\
														&K_1^{00}<K_2^{10}\;or\;K_1^{01}<K_2^{10}\;or\;K_1^{11}<K_2^{10}\;or\;\\
														&K_1^{00}<K_2^{01}\;or\;K_1^{01}<K_2^{01}\;or\;K_1^{11}<K_2^{01}\;or\;\\
														&K_1^{00}<K_2^{11}\;or\;K_1^{01}<K_2^{11}\;or\;K_1^{11}<K_2^{11}\;or\;\\
														&K_1^{00}<K_2^{21}\;or\;K_1^{01}<K_2^{21}\;or\;K_1^{11}<K_2^{21}\\
			{\tt All(v1<=v2[v1] < v1<=v2[v2])}\equiv\quad&    K_1^{00}<K_2^{00}\;and\;K_1^{01}<K_2^{00}\;and\;K_1^{11}<K_2^{00}\;and\;\\
														&K_1^{00}<K_2^{10}\;and\;K_1^{01}<K_2^{10}\;and\;K_1^{11}<K_2^{10}\;and\;\\
														&K_1^{00}<K_2^{01}\;and\;K_1^{01}<K_2^{01}\;and\;K_1^{11}<K_2^{01}\;and\;\\
														&K_1^{00}<K_2^{11}\;and\;K_1^{01}<K_2^{11}\;and\;K_1^{11}<K_2^{11}\;and\;\\
														&K_1^{00}<K_2^{21}\;and\;K_1^{01}<K_2^{21}\;and\;K_1^{11}<K_2^{21}\\
			\end{array}

.. _appendixB_identities:

Predicate Type 2: Identities
*****************************
Identity constraints enforce some - or all - values of a set of parameters to be equal.

	**Syntax**

	.. productionlist::
		identity: `quantifier` 'Identical(' `parameter_reference` ')'
		quantifier: ('All' | 'Some')

	**Semantics**

	Let :math:`\{K_i^{c_1},K_i^{c_2},\dots,K_i^{c_r}\}` be the referenced parameters. Depending on the quantifier, the equivalent low-level constraints are:

	.. math::
		\begin{array}{ll}
		\textrm{Quantifier}&	\textrm{Low-level constraint}\\
		\hline\hline
		\textrm{All}:&			K_i^{c_1}=K_i^{c_2}\;and\;K_i^{c_2}=K_i^{c_3}\;and\;\dots\;and\;K_i^{c_{r-1}}=K_i^{c_r}\\
		\textrm{Some}:&		K_i^{c_1}=K_i^{c_2}\;or\;\dots\;or\;K_i^{c_1}=K_i^{c_r}\;or\;K_i^{c_2}=K_i^{c_3}\;or\;\dots\;or\;K_i^{c_{r-1}}=K_i^{c_r}
		\end{array}

	:doc:`Running example <running_example>`: Let us consider the state formula :math:`v_1\leq v_2`. The parameter reference for :math:`v_1` is: :math:`K_1[v_1\leq v_2]=\{K_1^{00}, K_1^{01}, K_1^{11}\}`. With the two quantifiers we can formulate two constraints. Their equivalent low-level constraints are:

		.. math::
				
			\begin{array}{ll}
			{\tt SomeIdentical(v1<=v2[v1])}\equiv\quad K_1^{00}=K_1^{01}\;or\;K_1^{00}=K_1^{11}\;or\;K_1^{01}=K_1^{11}\\
			{\tt AllIdentical(v1<=v2[v1])}\equiv\quad K_1^{00}=K_1^{01}\;and\;K_1^{01}=K_1^{11}
			\end{array}

.. _appendixB_multiplexes:

Predicate Type 3: Multiplexes
*****************************
A multiplex constraint imposes a partition on the parameters of a specified component. Parameters in the same block of the partition *belong together* in the sense that they must all be equal. The partition is implicitly defined by specifying a list of state formulas, called *multiplexes* in this context. The procedure that achieves the partition of the parameters is then: For each state formula :math:`\psi_i^c` of a context of the specified component, compute the subset of the given state formulas that intersect :math:`\psi_i^c`. The blocks of the partition are then defined to consist of those Kinetic parameters that intersect the *same subset* of state formulas. For a publication on multiplexes see Section "Thomas’ Modelling with Multiplexes" in [Khalis09]_.

	**Syntax**

	.. productionlist::
		multiplex: 'Multiplex(' `state_formula` {',' `state_formula`} ':' `component` ')'

	**Semantics**

	Let :math:`\phi_1,\dots,\phi_p` be the given state formulas and :math:`v_i` the specified component. Let :math:`\tau_1,\dots,\tau_{2^p}` be the :math:`2^p` state formulas where :math:`\tau_i:\equiv\quad \phi_1'\;and\;\dots\;and\;\phi_p'` are all possible conjunctions of either :math:`\phi_i':\equiv\quad \phi_i` or :math:`\phi_i':\equiv\quad\;not\;\phi_i`. The equivalent of a :token:`multiplex` constraint in terms of :token:`identity` constraints is then:

	.. math::
		{\tt AllIdentical(\tau_1[v_i])\;and\;\dots\;and\;AllIdentical(\tau_{2^p}[v_i])}

	:doc:`Running example <running_example>`: Let us consider the multiplexes :math:`\phi_1:\equiv\quad v1=1\;and\;v2=2` and :math:`\phi_2:\equiv\quad v1=2`. With the following definitions of the state formulas :math:`\tau_i`:

		.. math::

			\begin{array}{l}
			\tau_1:\equiv\quad v1=1\;and\;v2=2, v1=2 : v_2\\
			\tau_2:\equiv\quad (not\;(v1=1\;and\;v2=2))\;and\;v1=2\\
			\tau_3:\equiv\quad v1=1\;and\;v2=2\;and\;(not\;v1=2)\\
			\tau_4:\equiv\quad (not\;(v1=1\;and\;v2=2))\;and\;(not\;v1=2)\\
			\end{array},

	the equivalent of the :token:`multiplex` constraint in terms of :token:`identity` constraints is:

		.. math::

			{\tt Multiplex(v1=1\;and\;v2=2, v1=2 : v_2)\equiv\quad AllIdentical(\tau_1[v_2])\;and\;\dots\;and\;AllIdentical(\tau_4[v_2])}	


	To compute the equivalent low-level constraint, we need the partition of the kinetic parameters of :math:`v_2`. To compute the partition, we need to list for every parameter formula :math:`\psi_2^c` those multiplexes that intersect its states:

		.. math::

			\begin{array}{lccc}
			\textrm{Parameters of }v_2&\textrm{Context states}&	\textrm{Intersection with }\phi_1&		\textrm{Intersection with }\phi_2\\
			\hline\hline
			K_2^{00}&				\{00,01\}&					\emptyset&								\emptyset\\
			K_2^{01}&				\{02\}&						\emptyset&								\emptyset\\
			K_2^{10}&				\{10,11\}&					\emptyset&								\emptyset\\
			K_2^{11}&				\{12\}&						\{12\}&									\emptyset\\
			K_2^{20}&				\{21,20\}&					\emptyset&								\{21,20\}\\
			K_2^{21}&				\{22\}&						\emptyset&								\{22\}
			\end{array}

	In this case we have a partition into 3 blocks: Those parameters that do no intersect either state formula, i.e., :math:`\{K_2^{00},K_2^{01},K_2^{10}\}`, those that only intersect :math:`\phi_1`, i.e., :math:`\{K_2^{11}\}`, and those that only intersect :math:`\phi_2`, i.e., :math:`\{K_2^{20},K_2^{21}\}`. There are no parameters that intersect both. The equivalent low-level constraints is therefore:

		.. math::

			 {\tt Multiplex(v1=1\;and\;v2=2, v1=2 : v_2)}\equiv\quad K_2^{00}=K_2^{01}\;and\;K_2^{01}=K_2^{10}\;and\;K_2^{20}=K_2^{21}


.. _appendixB_edge_labels:

Predicate Type 4: Edge Labels
*****************************
Edge labels constrain the effect, that a regulator has on its target. With *circuit functionality*, they were one of the first constraints to be considered by Thomas and Thieffry and are essential to the *Thomas conjectures* about feedback loops and attractors in the transition graph. Originally, the labels enforced a *monotonicity* in the target values (see for example Def. 4 and Sec. 5 in [Bernot04]_). Later, *observability* was added to the edge label constraints (see Sec. 4.2 in [Richard05]_).

	**Syntax**

	.. productionlist::
		edge_label: `label` '(' `name` ',' `name` , `threshold` [',' `state_formula`] ')'
		label: 'Observable' | (('Activating' | 'Inhibiting') ['Only'])

	**Semantics**

	Let :math:`v_i` be the regulator (the first *name* argument), :math:`v_j` be the target (the second *name* argument),
	:math:`t\in\theta(v_iv_j)` be a threshold of the interaction :math:`v_iv_j` and :math:`\phi` be a state formula of an :token:`edge_label` constraint. If the optional state formula is omitted, it is taken to be :math:`True`. Let

	.. math::
		K_j[\phi\;and\;v_i=t]:=\{K_j^{c_1},K_j^{c_2},\dots,K_j^{c_r}\}

	be the parameters of :math:`v_j`, referenced by :math:`\phi\;and\;v_i=t`. For each context :math:`c_i` we denote by :math:`c_i'` the unique context obtained from :math:`c_i` by lowering the intensity of the interaction :math:`v_iv_j` by one. (Recall that a context is a tuple consisting of :ref:`interaction intensities <appendixA_interaction_intensities>`).

	The low-level equivalent of the edge labels *Activating* and *Inhibiting* are then defined by:

	.. math::
		\begin{array}{l@{\quad:\quad}l}
		\textrm{Label}&			\textrm{Low-level constraint}\\
		\hline\hline
		\textrm{Activating}&	K_j^{c_1}>K_j^{c_1'}\;or\;K_j^{c_2}>K_j^{c_2'}\;or\;\dots\;or\;K_j^{c_r}>K_j^{c_r'}\\
		\textrm{Inhibiting}&	K_j^{c_1}<K_j^{c_1'}\;or\;K_j^{c_2}<K_j^{c_2'}\;or\;\dots\;or\;K_j^{c_r}<K_j^{c_r'}\\
		\end{array}

	The other edge labels are convenient shortcuts for logical combinations of *Activating* and *Inhibiting*:

	.. math::
		\begin{array}{ll}
		\textrm{Label}&			\textrm{Equivalent constraint}\\
		\hline\hline
		\textrm{Observable}&	\textrm{Activating}\;or\;\textrm{Inhibiting}\\
		\textrm{ActivatingOnly}&\textrm{Activating}\;and\;not\;\textrm{Inhibiting}\\
		\textrm{InhibitingOnly}&\textrm{Inhibiting}\;and\;not\;\textrm{Activating}\\
		\end{array}

	The optional state formula restricts the referenced parameters. With it we can control *where in state space* we want to see the interaction effect.

	:doc:`Running example <running_example>`: Let us consider a couple of examples.

	First an example without a state formula: :math:`{\tt Activating(v_1, v_2, 1)}`.
	The referenced parameters are :math:`K_2[True\;and\;v_1=1]=\{K_2^{10},K_2^{11}\}`.
	The equivalent low-level constraint is therefore:

	.. math::
		{\tt Activating(v_1, v_2, 1)}\equiv\quad K_2^{10}>K_2^{00}\;or\;K_2^{11}>K_2^{01}.

	Now an example with a state formula: :math:`{\tt Inhibiting(v_2, v_2, 2, v_1>0)}`.
	The referenced parameters are :math:`K_2[v_1>0\;and\;v_2=2]=\{K_2^{11},K_2^{21}\}`.
	The equivalent low-level constraint is therefore:

	.. math::
		{\tt Inhibiting(v_2, v_2, 2, v_1>0)}\equiv\quad K_2^{11}<K_2^{10}\;or\;K_2^{21}<K_2^{20}.

	Finally an example of a convenience edge label: :math:`{\tt Observable(v_2, v_1, 1, v_1>0)}`
		
	.. math::
		{\tt Observable(v_2, v_1, 1, v_1>0)\equiv\quad Activating(v_2, v_1, 1, v_1>0)\;or\;Inhibiting(v_2, v_1, 1, v_1>0)}.


.. noch hinzuzufügen

	Predicate Type X: Circuit Functionality
	**************************************

.. _appendixB_subgraphs:

Predicate Type 5: Subgraphs
****************************
These constraints enforce the existence of a subgraph in the :ref:`asynchronous state transition graph<appendixA_async_dynamics>`. We have implemented a general :token:`subgraph` and a :token:`path` predicate. 

	**Syntax**

	.. productionlist::
		subgraph: 'ContainsSubgraph(' `transitions` {',' `transitions`})'
		transitions: `state` ': [' `states` ']
		path: 'ContainsPath(' `states` ')'
		states: `state` {',' `state`}
		state: `activity` {`activity`}
		activity: 0 | 1 | ...

	**Semantics**
	
	*Subgraph*: We use the successor-based description of directed graphs as an argument for the :token:`subgraph` constraint.
	A transition therefore consists of a tail :token:`state`, followed by a semicolon and a list of successor states. We denote a state by a tuple of activities, given in concise notation without brackets or commata, where the :math:`i^{th}` activity refers to component :math:`v_i`.

	An *example* of the syntax of a successor-based description of the 3 unitary and asynchronous transitions :math:`\{(01002,11002),(01002,01102),(01002,01003)\}` is:

	.. math::
		01002 : [11002,01102,01003]

	We denote the state formula referencing a single state :math:`x\in X` by
	
	.. math::
		\phi_x:\equiv\quad v_1=x_1\;and\;\dots\;and\;v_n=x_n.

	For every transition :math:`(x,y)\in T` of an asynchronous state transition graph :math:`(X,T)`, there is a unique index :math:`k(x,y)`, such that :math:`x_k\neq y_k`. 
	For each tail state :math:`x\in X` and each of its successors :math:`y\in X` there is a unique index :math:`k(x,y)`, such that :math:`x_k\neq y_k`. The single parameter that causes the transition is therefore :math:`K_k[\phi_x]=\{K_k^c\}`. If :math:`x_k<y_k` we enforce the low-level constraint:

	.. math::
		K_k^c>x_k

	Otherwise, if :math:`x_k>y_k` we enforce the low-level constraint:

	.. math::
		K_k^c<x_k

	*Path*: A :token:`path` constraint is just a special case of a :token:`subgraph` constraint with simplified syntax, i.e., by just passing a comma seperated list of the path states in sequence to the predicate.

	:doc:`Running example <running_example>`: If we want to make sure that the transitions :math:`\{(00,01),(00,10),(10,00)\}` are contained in the transition graph of a model, we enforce the constraint :math:`{\tt ContainsSubgraph(00:[01,10],10:[00])}`. The equivalent low-level constraint is:

	.. math::
		{\tt ContainsSubgraph(00:[01,10],10:[00])}\equiv\quad K_1^{00}>0\;and\;K_2^{00}>0\;and\;K_1^{10}<1

	The low-level equivalent of a :token:`path` constraint, for the existence of the path :math:`(00,10,00)` in the transition graph, is:

	.. math::
		{\tt ContainsPath(00,10,00)}\equiv\quad K_1^{00}>0\;and\;K_1^{10}<1

.. _appendixB_comparisons:
		
Predicate Type 6: Comparisons
******************************
The comparison predicate is different to the other constraints, defined above, in that it requires the specification of a particular parametrization. It is therefore not applicable to :doc:`section1`. Instead, it is included especially for the :ref:`custom classifiers <section2_custom_classifier>` of :doc:`section2`. During the classification loop, a particular parametrization :math:`P` is retrieved from the model database. A :token:`compare` constraint is similar to a :token:`inequality_abs` constraint. Instead of specifying a constant number for the right-hand side of the inequalities, the corresponding target values of the given parametrization :math:`P` are substituted.

	**Syntax**	

	.. productionlist::
		compare: `quantifier` 'Compare(' `parameter_reference` ':' `operator` ')'

	**Semantics**

	Let :math:`P` be the specified parametrization, :math:`\{K_i^{c_1},K_i^{c_2},\dots,K_i^{c_r}\}` be the referenced parameters and :math:`\star\in\{<,\leq,=,\geq,>,\neq\}` the given operator. Depending on the :token:`quantifier`, the low-level equivalent of a :token:`compare` constraint is:

	.. math::
		\begin{array}{ll}
		\textrm{Quantifier}&	\textrm{Low-level constraint}\\
		\hline\hline
		\textrm{All}&			K_i^{c_1}\star P_i^{c_1}\;and\;K_i^{c_2}\star P_i^{c_2}\;and\;\dots\;and\;K_i^{c_r}\star P_i^{c_r}\\
		\textrm{Some}&			K_i^{c_1}\star P_i^{c_1}\;and\;K_i^{c_2}\star P_i^{c_2}\;and\;\dots\;and\;K_i^{c_r}\star P_i^{c_r}
		\end{array}
		

	:doc:`Running example <running_example>`: Suppose the specified parametrization is:

	.. math::
		P_1^{00}=0,P_1^{01}=1,P_1^{10}=2,P_1^{11}=0,P_2^{00}=2,P_2^{01}=1,P_2^{10}=1,P_2^{11}=0,P_2^{20}=2,P_2^{21}=0.

	Here are two examples of a :token:`compare` constraint:

	.. math::
		\begin{array}{l}
		{\tt AllCompare(v_1=2[v_2]:\;=)}\equiv\quad K_2^{20}=2\;and\;K_2^{21}=0\\
		{\tt SomeCompare(True[v_1]:\;\neq)}\equiv\quad K_1^{00}\neq0\;or\;K_1^{01}\neq1\;or\;K_1^{10}\neq2\;or\;K_1^{11}\neq0
		\end{array}















