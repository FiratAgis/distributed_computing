.. include:: substitutions.rst

Implementation, Results and Discussion
======================================

Implementation and Methodology
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Both Peterson's :ref:`Algorithm <PetersonsAlgorithm>` [Peterson1981]_ and Bakery :ref:`Algorithm <BakeryAlgorithm>` [Lamport1974]_ use central registers for the decision of which process is supposed to move forwards (turn and waiting for Peterson's Algorithm, entring and ticket for Bakery Algorithm, see Section XX for more details). Because of the following reasons, I gave the management responsibility of these registers to a single centralized entity instead of giving several entities shared access to them:

1. Accessing or modifying data across a topology in a distributed system might have significant latency problems.

2. These algorithms are already trying to resolve the problem of managing a shared memory; because of this, their implementation should not produce the same problem recursively.

This decision created a need for another decision to be made: what should be the nature of this central entity? Specifically, should it be a separate kind of entity or one of the entities that have access to the shared memory? To minimize the number of entities in the topology, I decided that it should be one of the processes that also wish to enter the critical section. However, this also creates several system limitations.

Firstly, while both components are designed in a way that they can leave and enter the topology because the tracking of the information required is on a single process, and transferring that responsibility is not in the scope of the algorithms, that process does not have the luxury of leaving. 

Following that, one entity must be reserved to manage access to the critical section. That is a major problem for Peterson's Algorithm, as it has a limit of two processes it can manage. While the locking system has a limit on the number of processes it can manage, determined at initialization due to implementation limitations, it has no theoretical limit in the case of the Bakery Algorithm. This makes it possible for the limit to be determined according to the fact that one of the entities must be reserved for managing the lock, elevating this problem for the practical uses of the Bakery Algorithm.

Thirdly, all topology is assumed to be a process that wants to access the critical section. This is once again a major limitation of Peterson's Algorithm, as this limits the topology to only two entities, one being the leader.

Lastly, both algorithms have no mechanism for determining the manager or leader for a more domain-appropriate term, which makes them rely on other components to handle the decision of leader election. 

These limitations are the main problems with the current implementations of the algorithms, but they are not solved at this time either because solving them requires the creation of new problems or because of time or expertise limitations. 


Results
~~~~~~~~

Present your AHCv2 run results, plot figures.


This is probably the most variable part of any research paper, and depends upon the results and aims of the experiment. For quantitative research, it is a presentation of the numerical results and data, whereas for qualitative research it should be a broader discussion of trends, without going into too much detail. For research generating a lot of results, then it is better to include tables or graphs of the analyzed data and leave the raw data in the appendix, so that a researcher can follow up and check your calculations. A commentary is essential to linking the results together, rather than displaying isolated and unconnected charts, figures and findings. It can be quite difficulty to find a good balance between the results and the discussion section, because some findings, especially in a quantitative or descriptive experiment, will fall into a grey area. As long as you not repeat yourself to often, then there should be no major problem. It is best to try to find a middle course, where you give a general overview of the data and then expand upon it in the discussion - you should try to keep your own opinions and interpretations out of the results section, saving that for the discussion.


.. image:: figures/CDFInterferecePowerFromKthNode2.png
  :width: 400
  :alt: Impact of interference power


.. list-table:: Title
   :widths: 25 25 50
   :header-rows: 1

   * - Heading row 1, column 1
     - Heading row 1, column 2
     - Heading row 1, column 3
   * - Row 1, column 1
     -
     - Row 1, column 3
   * - Row 2, column 1
     - Row 2, column 2
     - Row 2, column 3

Discussion
~~~~~~~~~~

Present and discuss main learning points.
