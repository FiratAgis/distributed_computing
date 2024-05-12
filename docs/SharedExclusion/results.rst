.. include:: substitutions.rst

Implementation, Results and Discussion
======================================

Implementation and Methodology
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Both Peterson's :ref:`Algorithm <PetersonsAlgorithm>` [Peterson1981]_ and Bakery :ref:`Algorithm <BakeryAlgorithm>` [Lamport1974]_ use central registers for the decision of which process is supposed to move forwards (turn and waiting for Peterson's Algorithm, entring and ticket for Bakery Algorithm, see Section XX for more details). Because of accessing or modifying data across a topology in a distributed system might have significant latency problems, and due to my lack of experience with distributed systems, I gave the management responsibility of these registers to a single centralized entity instead of giving several entities shared access to them, resembling their implementations for single processor systems. While this eleminates their main improvements to the field and reduce their failure proofness, it improves the messaging complexity of the Bakery Algorithm from O(n) to O(1).

This decision created a need for another decision to be made: what should be the nature of this central entity? Specifically, should it be a separate kind of entity or one of the entities that have access to the shared memory? To minimize the number of entities in the topology, I decided that it should be one of the processes that also wish to enter the critical section. However, this also creates several system limitations.

Firstly, while both components are designed in a way that they can leave and enter the topology because the tracking of the information required is on a single process, and transferring that responsibility is not in the scope of the algorithms, that process does not have the luxury of leaving. 

Following that, one entity must be reserved to manage access to the critical section. That is a major problem for Peterson's Algorithm, as it has a limit of two processes it can manage. While the locking system has a limit on the number of processes it can manage, determined at initialization due to implementation limitations, it has no theoretical limit in the case of the Bakery Algorithm. This makes it possible for the limit to be determined according to the fact that one of the entities must be reserved for managing the lock, elevating this problem for the practical uses of the Bakery Algorithm.

Thirdly, all topology is assumed to be a process that wants to access the critical section. This is once again a major limitation of Peterson's Algorithm, as this limits the topology to only two entities, one being the leader.

Lastly, both algorithms have no mechanism for determining the manager or leader for a more domain-appropriate term, which makes them rely on other components to handle the decision of leader election. 

These limitations are the main problems with the current implementations of the algorithms, but they are not solved at this time either because solving them requires the creation of new problems or because of time or expertise limitations. 


Results
~~~~~~~~

I tested my implementation of the Peterson's Algorithm, but because of its limited nature, it does not lend itself to different kinds of setups.

For my implementation of the Bakery Algorithm, I tested it for
1. Well-connected topologies ($O(n^2)$ connections)
2. Topologies where only connections are between the leader and others.
3. Two directional ring topologies without shortcuts.
4. One-directional ring topologies without shortcuts.

However, due to the topology-independent nature of the algorithm as well as the details of my implementation, those only tested the robustness of my forwarding. I was unable to test the failure resistance of the algorithms as my implementation was lacking on that front. If implemented in the future, testing my implementations against more faithful incarnations of the same algorithms could result in more interesting results. Due to these, I was unable to produce a quantitative experiment. But I tested that both implementations actually work.

