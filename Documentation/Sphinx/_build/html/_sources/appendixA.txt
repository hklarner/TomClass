Appendix A: Finite Dynamical Systems
####################################
.. _appendixA_background:

Background: Finite Dynamical Systems
************************************
Finite dynamical systems consist of a finite set :math:`X`, called *state space*, and a function :math:`f:X\rightarrow X`, called *update function*. For any state :math:`x\in X` we can then study the trajectory :math:`x,f(x),f^2(x),f^3(x),\dots` that unfolds by the given function. An immediate observation is that, since :math:`X` is finite, every trajectory is finite in the sense that it must end in a cycle of some length :math:`k\geq 1`, where cycles of length 1 are called *steady states* and cycles of length at least 2 are called *cyclic attractors*. The union of steady states and cyclic attractors makes the set of *attractors* of the system :math:`(X,f)`. Of course, the trajectories of two different states may end up in the same attractor. It is therefore not easy to predict how many different attractors there are in a given system.

In 1969 Stuart Kauffman published a study that applied finite dynamical systems ideas to modelling the dynamics of gene regulatory networks (see [Kauffman69]_). 
Kauffman modelled gene products with Boolean variables, that encode whether the respective product is present or not. Regulatory effects were abstracted to Boolean functions that calculate the state of a product from the state of its regulators.
Kauffman computed trajectories of randomly generated Boolean networks and counted the number of different attractors. His findings suggest that there are roughly as many attractors in a Boolean network of :math:`n` variables, as there are different cell types in an organism with a genome consisting of :math:`n` genes.

The particular difficulty one faces when modelling regulatory networks is that the function :math:`f` is not known. Instead, a graph structure underlying the function is assumed, usually obtained by reverse engineering techniques, and the set of functions that is compatible with the graph structure is considered feasible. In the following sections we discuss the graph structure, called *regulatory graph*, the set of functions that are compatible, called the *parametrizations of a regulatory graph* and the *asynchronous and unitary* update stategy, that is used to describe the dynamics, i.e., the *state transition graph* of a parametrization.

	**Table of contents of Appendix A**

	* :ref:`appendixA_reg_graphs`
	* :ref:`appendixA_state_space`
	* :ref:`appendixA_parametrizations`
	* :ref:`appendixA_async_dynamics`

.. hm
		A first approximation to the state of a gene product is whether it is present (1) and not present (0).
		Moreover, interactions between elements can be abstracted by Boolean functions which calculate the state of a gene product from the 		state of the regulating products.
		Boolean networks became popular by a study of S. Kauffman in 1969.

		The dynamics of a Boolean network is described by as many Boolean functions as there are genes.
		The structure of a Boolean network can be given in the form of a wiring diagram consisting of two layers:
		The first one consist of the n genes and represents the inputs to the second one, which also consists of the n genes.
		Underneath each gene in the second layer, its update function is given.

		The update from one state to the next is usually determined in a parallel fashion.
		Transitions are therefore deterministic: each state has exactly one successor.
		A sequence of states obtained by applying the update rules is called trajectory.
		All trajectories eventually reach a steady state (point attractor) or cycle (dynamic attractor).
		States that are not part of an attractor are called transient.
		Attractors and transient states that lead to it constitute basins of attraction.

		Boolean networks make strong simplifying assumptions: gene products are either present or not, intermediate expression levels are 			neglected.
		Also transitions between the activation states of genes are assumed to occur synchronously.
		This is usually not the case and hence certain behaviors may not be predicted by the simulation. 

.. _appendixA_reg_graphs:

Regulatory graphs
*****************
The components :math:`V=\{v_1,\dots,v_n\}` that are involved in a regulatory network and their dependecies
can be captured in directed graph :math:`(V,E)`. An arc :math:`v_iv_j\in E\subseteq V\times V` is called an interaction.
The predecessors :math:`N^-(v_i):=\{v_j\in V\;|\; v_jv_i\in E\}` are called regulators of :math:`v_i`, and its successors :math:`N^+(v_i)`
are called targets of :math:`v_i`.

	:doc:`Running example <running_example>`: As a running example, consider the complete graph of two components :math:`V=\{v_1,v_2\}`:

	.. image::  images/appendix_A_01.jpg
		:scale: 50 %
		:align: center

Since we are not only interested in the structure of the network but also in
its dynamics, we interpret the components as integer variables whose values signify
the level of activity, e.g. the concentration level, of the corresponding substance.
Naturally, the impact a regulator has on its target depends on the regulators activity.
To define a model of the networks dynamics we therefore have to specify a set of activity levels for each component, and interaction thresholds, that allow us to distinguish the effects that a regulator has on its target.
Since we are interested in finite dynamical systems, every component must have a maximal activity level and all interaction thresholds originating in it must lie below that maximal value.
This leads to the following definition:

	**Regulatory graph**

	A regulatory graph :math:`\mathcal R=(V,E,\rho,\theta)` consists of components :math:`V`, interactions :math:`E` and
	two functions :math:`\rho` and :math:`\theta`.
	The function :math:`\rho : V \rightarrow \mathbb N_1` assigns a non-zero number :math:`\rho(v_i)`,
	called *maximal activity level* of :math:`v_i`, to each component.
	The other function, :math:`\theta`, assigns interaction thresholds :math:`\theta(v_iv_j)=(t_1,\dots,t_m)` to each interaction :math:`v_iv_j\in E`.
	The thresholds must be ordered: :math:`t_1<\dots< t_m` and within the set of non-zero activities of the regulator:
	:math:`1\leq t_1` and :math:`t_m\leq\rho(v_i)`.

We call :math:`m` the multiplicity of the interaction, a concept first introduced in Section 2 of [Chaouiya03]_.
The condition that thresholds must be greater than 0 is required,
because we want regulators to be able to fall below each of their interaction thresholds.
Although there is no restriction on the value of the maximal activity of a component, it is common to choose a value which is at most equal to the number of targets of that component.
A component that has two targets does therefore not usually have a maximal activity level equal to 3. 

.. _appendixA_running_example:

	:doc:`Running example <running_example>`: We choose the thresholds and maximal activities to be

	.. math::
		\begin{array}{llll}
		\rho(v_1)=&2&\theta(v_1v_1)=&(1)\\
		\rho(v_2)=&2&\theta(v_1v_2)=&(1,2)\\
		&&\theta(v_2v_1)=&(1)\\
		&&\theta(v_2v_2)=&(2)
		\end{array}.

	In the drawing of the regulatory graph, we label nodes with component name and activity interval, and interactions with thresholds:

	.. image::  images/appendix_A_02.jpg
		:scale: 50 %
		:align: center

.. _appendixA_state_space:

State space and state formulas
******************************
To a regulatory graph :math:`\mathcal R` we associate the state space

.. math::
	X:=\prod_{i=1}^n[0..\rho(v_i)].

An element :math:`x\in X` is called a state of the regulatory graph and we use the
subscript notation :math:`x_i` to denote the activity of :math:`v_i\in V` in state :math:`x`.
Since the state space is a cartesian product, it can naturally be arranged to form a grid with as many dimensions as there are components.

	*Example*: We give two examples: The 2-component regulatory graph of the :doc:`Running example <running_example>` and its state space, arranged in a 2-dimensional grid,

	.. image:: images/appendix_A_03.jpg
		:scale: 50%
		:align: center

	and a 3-component regulatory graph and its state space, arranged in a 3-dimensional grid:

	.. image:: images/appendix_A_04.jpg
		:scale: 50%
		:align: center

When we discuss the :ref:`dynamics <appendixA_async_dynamics>` of a regulatory graph, we will assign behaviors the descriptions of the system. We might, for example, say: If the activity of component :math:`v_2` is greater or euqal to :math:`1`, then the activity of its target :math:`v_1` will tend to :math:`0`. 
The first part of this statement, "If the activity of :math:`v_2` is greater or euqal to :math:`1`", is a description of the state of the system. We can then enumerate all states to which this description applies.
Therefore, a system description implicitly defines a subset of the state space.

It is convenient to formalise system-descriptions by means of a language.
The atomic statements in this language are inequalities regarding the component activities.
These can be combined by logic operators to form more complex formulae, that we call "state formulas".

As a remark: This is analogous to the "propositional logic formulae over AP" in model checking (see e.g. A.3 in [Baier08]_).
Before we define the *state formula* syntax, let us take a look at some examples:

	:doc:`Running example <running_example>`: We give three examples to illustrate how state formulas, i.e.,  system descriptions, define subsets of the state space.
	States to which the description applies are enclosed in gray boxes.

	.. image:: images/appendix_A_05.jpg
		:scale: 50%
		:align: center

Now to the formal definitions of the syntax.

.. _appendixA_state_formulas:

	**State formulas**

	Let :math:`(V=\{v_1,\dots,v_n\},\rho)` be the components and maximal activities of the considered state space :math:`X`, with :math:`M:=\max_{v_i\in V}\{\rho(v_i)\}` the overall maximal activity level.
	We associate a finite set of atomic propositions :math:`AP` to :math:`(V,M)`, that consists of all *component inequalities* together with the proposition *True*:

	.. productionlist::
		atom: `component` `operator` `component` | `component` `operator` `activity` | 'True'
		component: 'v1'|'v2'|...|'vn'
		activity: '0'|'1'|'2'|...|'M'
		operator: '<'|'<='|'='|'>='|'>'|'!='

	State formulas are defined to be propositional logic formulas over the atomic propositions:

	.. productionlist::
		state_formula: `atom` | 'not' `state_formula` | `state_formula` 'and' `state_formula` | `state_formula` 'or' `state_formula`

	We can *evaluate* a formula :math:`\phi`, i.e., turn it into a subset of :math:`X`, by writing :math:`X[\phi]`.
	A state :math:`x\in X` belongs to the evaluation of :math:`\phi`, i.e. :math:`x\in X[\phi]`, if the Boolean expression, obtained from :math:`\phi` by replacing the component names with the activities of :math:`x`, evaluates to true.
	If :math:`x\in X[\phi]` we say that :math:`x` is referenced by :math:`\phi`.
	The atom :math:`True` is used to reference *all states*, i.e., :math:`X[True]=X`.

	:doc:`Running example <running_example>`: The state :math:`(0,2)` belongs to the evaluation of the formula :math:`v_1<v_2\;or\;v_2=0`, because the Boolean expression obtained from the formula by replacing the component names with the activities of the state is :math:`0<2\;or\;2=0`, which is true.
	

Note that taking the union of the evaluations of two formulas :math:`X[\phi_1]\cup X[\phi_2]` is equivalent to evaluating the disjunction :math:`X[\phi_1\;or\;\phi_2]`. Similarly,

	.. math::

		X[\phi_1] \cap X[\phi_2] = X[\phi_1\;and\;\phi_2].



.. _appendixA_parametrizations:

Parametrizations
****************
In this subsection we discuss how to parametrize a regulatory graph.
A parametrization allows us to determine all transitions between states and thus study the dynamics of a regulatory network.
A parametrization provides all the information necessary to determine the combined effect of components on their targets in every state.
The effect will not necessarily depend on the exact component activities of a considered state,
but only on the regulation thresholds that are surpassed in this state.
We formalize this idea in the following concepts.

.. _appendixA_interaction_intensities:

	**Interaction intensities**

	The thresholds :math:`\theta(v_iv_j)=(t_1,\dots,t_m)` of an interaction :math:`v_iv_j` divide the effect of the regulator :math:`v_i` on 
	its target :math:`v_j` into :math:`m+1` cases of *different intensity*,
	denoted by :math:`I(v_iv_j)=\{0,1,\dots,m\}`. To each intensity :math:`i\in I` we associate a state formula :math:`\psi_{v_iv_j}^i`:

.. math::
	\begin{array}{l|lll}
	\textrm{Intensity}&\multicolumn{3}{c}{\textrm{State formula}} \\
	\hline
	0&\psi_{v_iv_j}^0:\equiv 0&\leq v_i<& t_1,\\
	1&\psi_{v_iv_j}^1:\equiv t_1&\leq v_i<& t_2,\\
	\dots&&\dots\\
	m-1&\psi_{v_iv_j}^{m-1}:\equiv t_{m-1}&\leq v_i<& t_m,\\
	m&\psi_{v_iv_j}^m:\equiv t_m&\leq v_i\leq& \rho(v_i)
	\end{array}.

The formula associated to intensity :math:`i\in I(v_iv_j)` references all states, where the regulators activity has surpassed :math:`i` thresholds of :math:`\theta(v_iv_j)`.
Therefore, every state of state space is referenced by *exactly one intensity formula*: the evaluated formulas form a partition of the state space.
In the simplest case an interaction has a single threshold. Such an interaction defines two intensities, namely 0 and 1,
and two formulas: the formula where the regulators activity is below the threshold, and the one where it is equal to or above it.

	:doc:`Running example <running_example>`: The table below lists all intensities and associated state formulas.

	.. math::
		\begin{array}{l|ll}
		\textrm{Interaction}&\textrm{Intensity}&\textrm{State formulas}\\
		\hline
		v_1v_1	& 0 & \psi_{v_1v_1}^{0}:\equiv 0\leq v_1<1\\
				& 1 & \psi_{v_1v_1}^{1}:\equiv 1\leq v_1\leq2\\
		\hline
		v_1v_2	& 0 & \psi_{v_1v_2}^{0}:\equiv 0\leq v_1<1\\
				& 1 & \psi_{v_1v_2}^{1}:\equiv 1\leq v_1<2\\
				& 2 & \psi_{v_1v_2}^{2}:\equiv 2\leq v_1\leq2\\
		\hline
		v_2v_1	& 0 & \psi_{v_2v_1}^{0}:\equiv 0\leq v_2<1\\
				& 1 & \psi_{v_2v_1}^{1}:\equiv 1\leq v_2\leq2\\
		\hline
		v_2v_2	& 0 & \psi_{v_2v_2}^{0}:\equiv 0\leq v_2<2\\
				& 1 & \psi_{v_2v_2}^{1}:\equiv 2\leq v_2\leq2\\
		\end{array}.

	The four images below illustrate the state space partitions for every interaction.
	States that have the same intensity with respect to an interaction are enclosed by gray boxes.
	The corresponding intensity of the interaction is indicated inside the blue circles:

	.. image:: images/appendix_A_06.jpg
		:scale: 50%
		:align: center

The intensities of an interaction give only an incomplete picture of a components regulation,
because the other regulators intensities are left unspecified.
A complete specification of the intensities of all regulators of a component is called a *regulatory context* of that component:

.. _appendixA_regulatory_context:

	**Regulatory context**

	Let :math:`d` be the number of regulators of a component :math:`v_i` and :math:`r_1<\dots<r_{d}` be their indices in :math:`V`.
	The regulatory contexts :math:`C_i` of :math:`v_i` are all combinations of assigning intensities to its regulators:
	
	.. math::
		C_i:=\prod_{j=1}^{d}I(v_{r_j}v_i).

As before with the levels of an interaction we identify each regulatory context of a component with a state formula :math:`\psi_i^c`.
We do this by taking the *conjunction* of the formulas associated to each regulators intensity in the context.
The formula associated to a context :math:`c=(i_1,i_2,...,i_d)` of component :math:`v_i` is therefore :math:`\psi_i^c:\equiv \phi_1\;and\;\phi_2\;...\;and\;\phi_d`,
where :math:`\phi_k` is the formula associated to intensity :math:`i_k`.

	:doc:`Running example <running_example>`: The table below lists all regulatory contexts and associated formulas.

	.. math::
		\begin{array}{l|ll}
		\textrm{Component}&\textrm{Context}&\textrm{State formula}\\
		\hline
		v_1		& 00 & \psi_1^{00}:\equiv 0\leq v_1<1		\textrm{ and } 0\leq v_2<1\\
				& 01 & \psi_1^{01}:\equiv 0\leq v_1<1		\textrm{ and } 1\leq v_2\leq2\\
				& 10 & \psi_1^{10}:\equiv 1\leq v_1\leq2	\textrm{ and } 0\leq v_2<1\\
				& 11 & \psi_1^{11}:\equiv 1\leq v_1\leq2	\textrm{ and } 1\leq v_2\leq2\\
		\hline
		v_2		& 00 & \psi_1^{00}:\equiv 0\leq v_1<1		\textrm{ and } 0\leq v_2<2\\
				& 01 & \psi_1^{01}:\equiv 0\leq v_1<1		\textrm{ and } 2\leq v_2\leq2\\
				& 10 & \psi_1^{10}:\equiv 1\leq v_1<2		\textrm{ and } 0\leq v_2<2\\
				& 11 & \psi_1^{11}:\equiv 1\leq v_1<2		\textrm{ and } 2\leq v_2\leq2\\
				& 20 & \psi_1^{20}:\equiv 2\leq v_1\leq2	\textrm{ and } 0\leq v_2<2\\			
				& 21 & \psi_1^{21}:\equiv 2\leq v_1\leq2	\textrm{ and } 2\leq v_2\leq2\\
		\end{array}.

As before with the intensities of an interaction, the evaluated formulas of the contexts of a component form a *partition of the state space*.

	:doc:`Running example <running_example>`: The two images below illustrate how the regulatory contexts of a component partition the state space. States belonging to the same part are enclosed by gray boxes.
	The intensities of the contexts are indicated inside the blue circles:

	.. image:: images/appendix_A_07.jpg
		:scale: 50%
		:align: center

A regulatory context is the fundamental building block of a components dynamics. It is what the component can *perceive* of the state of the system.
As this description suggests, a components dynamics must be identical in every state that belongs to the same regulatory context. The dynamical behavior, or what the component *does* in a state of the system, is determined by assigning a target activity value to each of its contexts.
It should be interpreted as a regulation tendency: It describes, in absolute terms, the activity towards which the component tends, if it is in the context.

Now, we define the *kinetic parameters* as a set of symbolic variables representing a component and one of its contexts.

.. _appendixA_kinetic_parameters:

	**Kinetic parameters**

	To a regulatory graph :math:`\mathcal R` we associate a set
	
	.. math::

		K_{\mathcal R}=\{K_i^{c}\;|\;v_i\in V,c\in C_i\}

	of symbolic variables, called *kinetic parameters*.
	Each kinetic parameter :math:`K_i^{c}` represents exactly one regulatory context :math:`c\in C_i` of one component :math:`v_i\in V`.
	To simplify notation, we use *concise tuple representation* for the contexts, i.e., :math:`K_1^{12}` instead of :math:`K_1^{(1,2)}`.

A regulatory graph has therefore :math:`\sum_{i=1}^n|C_i|` kinetic parameters.
The running example has :math:`4+6=10` parameters.
Finally, we can define an assignment, called *parametrization*, of target values to the kinetic parameters:

	**Parametrization**

	Let :math:`m:=\max\{\rho(v_i)\;|\;v_i\in V\}` be the maximum of all maximal activities. A function :math:`P:K_{\mathcal R}\rightarrow [0..m]`, that assigns target values :math:`P(K_i^c)` to the kinetic parameters :math:`K_i^c`, such that

	.. math::

		\forall v_i\in V:\;\forall c\in C_i:\;\; P(K_i^c)\in [0..\rho(v_i)],

	is called a *parametrization* of a regulatory graph :math:`\mathcal R`. To simplify notation, we use :math:`P_i^c` to denote :math:`P(K_i^c)` and use *concise tuple representation* for the contexts.

We can easily count the number of distinct parametrizations for a regulatory graph. A regulatory graph has

.. math::
	\prod_{i=1}^n (\rho(v_i)+1)^{|C_i|}

different parametrizations. The running example has :math:`3^4\times 3^6=59\;049` parametrizations.

How are parametrizations used to study the dynamics of a regulatory graph? We can turn them into update functions: As a consequence of the observation that the regulatory contexts of a component form a partition of the state space, every state falls into *exactly one context of each component*. A parametrization is therefore unambiguous when it comes to the target value of a component in a state. Since this is true for every component, a parametrization defines a function on the state space: Each state is mapped to the state consisting of the respective target values. We can therefore interpret a parametrized regulatory graph as a finite dynamical system as introduced above, in the :ref:`Section: Background <appendixA_background>`.

	:doc:`Running example <running_example>`: The state :math:`(0,2)` falls into context :math:`(0,1)` of component :math:`v_1` and context :math:`(0,1)` of :math:`v_2`. The function :math:`F_P:X\rightarrow X`, derived from a parametrization :math:`P`, then defines the following image for state :math:`(0,2)`:

	.. math::
	
		F_P(0,2)=(P_1^{01},P_2^{01}).


.. datatype

	As a data type for storing parametrizations on a computer, we choose to list the target value of each :math:`P_i^c` as one long tuple, i.e., as an *integer vector of appropriate length*.
	To be unambiguous we must of course choose an order for listing the target values: We impose the *lexical order* on the component index, followed by the intensities of the regulatory contexts of the component

.. _appendixA_async_dynamics:

Asynchronous dynamics
*********************
The dynamics of pair :math:`(\mathcal R, P)` is captured in a so-called state transition graph.
It is a directed graph :math:`(X,T)` where :math:`X` is the state space and :math:`T\subset X\times X` is a set of transitions derived from the parametrization by certain update rules. The update rules of the networks introduced in :ref:`Section: Background<appendixA_background>` are one example. They are synchronous, i.e., components are updated in parallel, and non-unitary, i.e., activities may instantly change to any level. Both are strong simplifications.

In a more realistic model, the time between the activation of a gene and its product reaching a certain concentration threshold is considered. Different components are then likely to have different synthesis and degradation rates. R. Thomas formalized this refinement and introduced the *fully asynchronous update rules* (see [Thomas91]_): During a transition, the activity of at most one component changes. If many components "want to change", we add alternative transitions to the transition graph. A state may then have several successor states and we end up with a *non-deterministic model*.

With the intention to employ finite dynamical systems in the search for steady states in systems of differential equations, R. Thomas and E.H. Snoussi introduced *unitary transitions*. An activity changes by either +1 or -1 during a transition, it does not "jump".

Four different combinations are possible to pair any of "synchronous, asynchronous" with any of "unitary, non-unitary". To illustrate the resulting transitions consider the state :math:`(0,0)` and assume that the parametrization we are working with computes the target state :math:`(2,2)`, i.e., :math:`P_1(00)=2,\;P_2(00)=2`. The image below has four parts, one for every type of update rule. Transitions are indicated by arrows.

	.. image:: images/appendix_A_10.jpg
		:scale: 60%
		:align: center

The transitions of the unitary asynchronous transition graph :math:`(X,T)` of a parametrized regulatory graph :math:`(\mathcal R, P)` are defined as follows. For every component and each of its regulatory contexts, we increase the activity of states in the context and below the target value by one, and decrease the activity of states above the target value by one. States where the activity of the considered component is equal to the target value are left steady. To simplify notation for unitary changes, we interpret states as *vectors* and use vector addition with :math:`e_i` the unit vector in direction :math:`i`.

	**Asynchronous transitions**

	For each context :math:`c\in C_i` of each component :math:`v_i`, let :math:`\psi(i,c)` be the corresponding :ref:`state formula <appendixA_state_formulas>`.
	We add the following transitions to :math:`T`:
		* Increase: For every state :math:`x\in X[\psi(i,c)\;and\;v_i<P_i^c]` add the transition :math:`(x,x+e_i)` to :math:`T`.
		* Decrease: For every state :math:`x\in X[\psi(i,c)\;and\;v_i>P_i^c]` add the transition :math:`(x,x-e_i)` to :math:`T`.
	
	Finally, we add a loop onto every state :math:`x\in X` that is left with out-degree 0 after the above procedure.
	Those states are called *steady states* or *fixpoints* of the state transition graph.

.. topic:: To do:

	* Illustration for adding transitions by the rules (1) and (2) for a single context of a single component.
	* Illustration of a STG for running example.
	* Discuss "normalization" of parametrizations for asynchronous transition graphs.
























