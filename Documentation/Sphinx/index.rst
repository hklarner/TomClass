Custom Classification for Discrete Regulatory Networks
######################################################

.. topic:: Project Information

	* See the <..> for download, installation and project status.
	* Contributors to the project are <..>.

This is the manual to the software project *Custom Classification for Discrete Regulatory Networks*.
It is a contribution to the challange of understanding the dynamics of components in *regulatory networks*.
Examples of regulatory networks are the circuit diagrams of the control of gene expression (see for example *Fig. 7-71, Chapter 7* in [Alberts07]_). These diagrams consist of boxes and arrows between them, where boxes represent genes and arrows represent transcriptional activation or repression.

The structure of regulatory networks is usually characterized by (1) numerous positive and negative feedback paths, consisting of the arrows, called *interactions*, between components, and (2) combinatorial regulation dependencies.
Predicting the dynamics of such systems is, without precise quantiative information, exceedingly complex.
Since 1969, when Stuart Kauffman published a study that suggested that qualitative approximations to the dynamics of randomly generated regulatory networks (see [Kauffman69]_) "behaved with great order and stability", discrete formalisms have stirred some interest.
In particular, Kauffman suggested that "the number of behaviors per network roughly predicts the number of cell types in an organism as a function of the number of its genes." and thus opened the door to discrete approaches of modelling regulatory networks.

Later, René Thomas and and El Houssine Snoussi established a connection between qualitative models and piece-wise linear differential equations (see e.g. [Snoussi89]_ and [Thomas91]_). Underlying both, Kauffman's and Thomas' qualitative models, are *discrete functions* that *respect* the structure of the regulatory network. Although finite, the number of functions that respect a given structure is large. Deciding if there is a function that exhibits a certain behavior - or more general: Distinguishing *classes of functions* that exhibit similar behaviors - has consequently become a challenge in the qualitative framework.

Computers tools like *SMBioNet* (`homepage <http://www.i3s.unice.fr/~richard/smbionet/>`_, see also [Khalis09]_), *GNBoX* (no homepage, see [Corblin09]_) and *SysBioX* (no homepage, see [Corblin12]_) perform tasks along those lines. The contributions of this computer tool are:

(1) A **unified framework** for the classification of discrete functions, that is independent of *update rules* and *classification properties*.
(2) The creation of a database for each project, that **organizes classification results**.
(3) An interface that facilitates the implementation of **custom classification algorithms**.
(4) A **high-level constraint language** that makes it easier to implement custom classifiers.


.. hmm images/index_figure1.jpg
	:scale: 60 %
	:alt: Schematic view of starting a new project.
	:align: center

Contents
********
The tasks that this tool performs fall into three sections.
First, a set of initial parametrizations is defined and stored in a database.
This step is performed once for a project, with the script ``new_project.py``, and is discussed in :doc:`section1`.
Then, a classifying algorithm and property are specified and passed to the script ``continue_project.py``, which annotates parametrizations with class labels.
Instructions on how to implement a custom classifyer and a description of the classifyers already implemented are given in :doc:`section2`.
The last part is :doc:`section3`.
Here we describe how a database of annotated parametrizations may be used for behaviour prediction and experimental design.

In :doc:`Appendix A<appendixA>` we recapitulate the generalized logical method of Thomas and colleagues.
In :doc:`Appendix B<appendixB>` we introduce a parameter contstraint language. Parameter constraints play a dual role in the workflow of the tool.
They appear as necessary conditions when initial parametrizations are specified, or as a selection language during the process of classifying. 
Finally, in :doc:`Appendix C<appendixC>` we apply the tool to various problems.

	**Table of Contents**

	.. toctree::
  		:maxdepth: 2
		:numbered:

  		section1
  		section2
  		section3
  		appendixA
  		appendixB
  		appendixC
		appendixT
		bibliography


Quickstart
**********

* Edit :literal:`preferences.py`: add line :literal:`minizinc_path=.....`
* Create a regulatory graph file :literal:`/InputFiles/reg7.txt`
* Create an initial constraints file :literal:`/InputFiles/reg7_init1.txt`
* Edit :literal:`new_project.py`::
	project_name='quickstart'
	regulatory_graph = 'reg7.txt'
	initial_constraints = 'reg7_init1.txt'
* Run :literal:`new_script.py`
* Check that new folder :literal:`/Projects/quickstart` has been created and that it contains 4 files:
	* :literal:`reg7.txt`
	* :literal:`reg7_init1.txt`
	* :literal:`quickstart.log`
	* :literal:`quickstart.db`















