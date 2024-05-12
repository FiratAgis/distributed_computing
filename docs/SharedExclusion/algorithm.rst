.. include:: substitutions.rst

SharedExclusion
=========================================

Background and Related Work
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Because both Peterson's :ref:`Algorithm <PetersonsAlgorithm>` [Peterson1981]_ and Bakery :ref:`Algorithm <BakeryAlgorithm>` [Lamport1974]_ are very old; I limited their comparisons to their contemporaries. I can not say for certain, as this is not my area of expertise, but comparing them with the nearly 50 years of progress since their conception would be fruitless. 

Their main contemporaries are proposed by Knuth (1966) [Knuth1966]_, deBruijn (1967) [deBruijn1967]_, Eisenberg and McGuire (1972) [Eisenberg1972]_, Dijkstra (1965) [Dijkstra1965]_ and  Dijkstra (1968) [Dijkstra1968]_. The main limitation of these algorithms is the fact that they are not designed in a way that can handle truly distributed systems, relying on a single point of failure. While the main design of Peterson's Algorithm and Bakery Algorithm exits to combat this shortcoming by way of each process keeping the information relevant to itself and resetting that information in the event of a failure, my implementation resembles the contemporaries more closely.

Distributed Algorithm: SharedExclusion
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

SharedExclusion is a collection of algorithms for mutual exclusion in shared distributed memory, specifically Peterson's :ref:`Algorithm <PetersonsAlgorithm>` [Peterson1981]_ and Bakery :ref:`Algorithm <BakeryAlgorithm>` [Lamport1974]_.   


Peterson's Algorithm
""""""""""""""""""""""""

Peterson's :ref:`Algorithm <PetersonsAlgorithm>` [Peterson1981]_ works for two processes, let's call them $p_0$ and $p_1$, and prevents both of them from entering the critical section at the same time. It achieves this by way of each process giving way to another. When the process comes to the critical section, it first allows the other process to continue to the critical section and only moves forward if the other is not currently trying to enter the critical section or if the other process finishes its work within the critical section. While it is a gentleman's way of handling shared memory exclusion, its main limitation lies in the fact that it only works for two processes. This can be circumnavigated by a cascading that gives way to action for processes arranged in a binary tree, but that will be explored later.

.. _PetersonsAlgorithm:

    .. code-block:: RST
        :linenos:
        :caption: Peterson's Algorithm [Peterson1981]_.
                
        bool turn ← false, waiting[n] for each process p_n where n in {0, 1}; 

        if p_i wants to enter the critical section 
            waiting[i] ← true;
            turn ← (1 - i) % 2;
			
            while waiting[1 - i] = true and turn = (1 - i) % 2
                no-op;
				
            p_i enters the critical section;
			
            p_i exits the critical section;
			
            waiting[i] ← false;
        end if

While many idea of the algorithm is simple, it is beneficial to get a line-by-line perspective.

* In line 1, two variables are initialized: turn and waiting.

    * turn is a boolean, or more precisely a binary integer, as it is used in the algorithm to determine which processes turn it is to enter the critical section. When turn = 0, it is p_0's turn and vice versa.
    * waiting is a boolean array with length two that determines if a process is waiting to enter the critical section or not. 

* In line 3, it is checked that if a process wants to enter the critical section. If not, no action needs to be taken.
* In line 4, the process establishes that it is waiting to enter the critical section
* In line 5, the process gives way to the other process.
* In lines 7-8, the process waits until either it is its turn to enter the critical section or the other process does not have any intention of entering the critical section at the time. When either one of these conditions is met, it proceeds.
* In lines 10-12, the process does whatever it needs to do in the critical section.
* In line 14, the process establishes that its work with the critical section is done, and it is no longer waiting to access the critical section.

Correctness
~~~~~~~~~~~

While Peterson's Algorithm cannot evict process from the critical section, as long as processes exit the critical section willingly, it has the following properties:

* Only one process can enter the critical section at a time:
* As soon as a process exits the critical section, the other can enter it.
* It allows access to the critical section to all processes who wish to enter it in FIFO order but does not enforce fairness regarding time spent in the critical section.

Complexity 
~~~~~~~~~~

* Space Complexity: Peterson's Algorithm works on a constant amount of processes and requires a constant amount of space, O(1).
* Algorithmic Complexity: Each process that attempts to enter the critical section checks the other one's intent; because there is only one other process, it has an algorithmic complexity of O(1).
* If managed by a leader, each process needs to send a message to establish its intent to enter, receive a message that gives it permission to enter, and send a message to inform the leader that it exited the critical section. Even with possible acknowledgments, it has the message complexity of O(1).

Bakery Algorithm
""""""""""""""""""""""""

Bakery :ref:`Algorithm <BakeryAlgorithm>` [Lamport1974]_ simulates the activity of waiting in a line in its namesake to get your order. Every process takes a ticket with a number on it. When their number flashes on the screen, they come and give their order. If two processes have the same number on their ticket, meaning they get their ticket in the same timeframe, the conflict is resolved through seniority, just like letting an elderly person go before you when both of you arrive at the same time.

.. _BakeryAlgorithm:

    .. code-block:: RST
        :linenos:
        :caption: Bakery Algorithm [Lamport1974]_.
                
        bool entering[n] for each process p_n; 
        int ticket[n] for each process p_n; 

        if p_i wants to enter the critical section 
            entering[i] ← true;
            ticket[i] ← max(ticket) + 1;
            entering[i] ← false;
			
            for j = 1 to n
                while entering[j]
                    no-op;
                while ticket[j] != 0 and (ticket[j] < ticket[i] or (ticket[j] = ticket[i] and j < i))
                    no-op;
            end for
            
            p_i enters the critical section;
            
            p_i exits the critical section;
			
            ticket[i] ← 0;
			
        end if
		
The slight complexity of the algorithm when compared with the Peterson's :ref:`Algorithm <PetersonsAlgorithm>`, which enables the Bakery Algorithm to serve any number of processes (n processes, identified by $p_i$, i in [1, n]), warrants a closer examination of the pseudocode.

* In line 1, entering is initialized. It is a boolean array with length n. It determines whether a process is trying to get a ticket in that timeframe or not.
* In line 2, the tickets array is initialized. It is an integer array with length n. It records the number on a process' ticket.
* In line 4, it is checked that if a process wants to enter the critical section. If not, no action needs to be taken.
* In lines 5-7, the process takes a ticket whose number comes after all processes that are currently waiting to enter the critical section, as it arrived later than them.
* In lines 9-14, the process waits,

    * if any process is currently trying to get a ticket, as tickets taken within close proximity of each other might have the same number on them due to context switches between read and write operations (lines 10-11).
    * if any process with a lower number on its ticket or a more senior process with the same number on its ticket is also waiting to enter the critical section (lines 12-13).

* In lines 16-18, the process does whatever it needs to do in the critical section.
* In line 20, the processes get rid of their ticket, allowing processes with tickets containing greater numbers to also get into the critical section.

Correctness
~~~~~~~~~~~

While the Bakery Algorithm cannot evict process from the critical section, as long as processes exit the critical section willingly, it has the following properties:

* Only one process can enter the critical section at a time:
* As soon as a process exits the critical section, the others can enter it.
* It allows access to the critical section to all processes who wish to enter it in FIFO order but does not enforce fairness regarding time spent in the critical section.


Complexity 
~~~~~~~~~~

* Space Complexity: If managed through a leader process, the Bakery algorithm requires entering and ticket arrays with size n, n being the number of processes. It has a space complexity of O(n).
* Algorithmic Complexity: Each process that attempts to enter the critical section checks the other ones' entering and ticket; for n processes, it has algorithmic complexity of O(n).
* If managed by a leader, each process needs to send a message to establish its intent to enter, receive a message that gives it permission to enter, and send a message to inform the leader that it exited the critical section. Even with possible acknowledgments, it has the message complexity of O(1).


.. [Lamport1974] L. Lamport, A new solution of Dijkstra’s concurrent programming problem, Communications of the ACM, 17(8), 1974, 453–455.
.. [Peterson1977] G. L. Peterson and M. Fischer, Economical solutions for the mutual exclusion problem in a distributed system, Proceedings of the 9th ACM Symposium on Theory of Computing, 1977, 91–97.
.. [Peterson1981] G. L. Peterson, Myths about the mutual exclusion problem, Information Processing Letters, 12, 1981, 115–116.
.. [Knuth1966] D.E. Knuth, Additional comments on a problem in concurrent programming control. Comm. Acre 9(5), 1966, 321-322.
.. [deBruijn1967] N.G. deBruijn, Additional comments on a problem in concurrent programming control Comm. ACM 10(3), 1967, 137-138.
.. [Eisenberg1972] Eisenberg, M.A., and McGuire, M.R. Further comments on Dijkstra's concurrent programming control problem. Comm. ACM 15(11), 1972, 999.
.. [Dijkstra1965] Dijkstra, E.W. Solution of a problem in concurrent programming control. Comm. ACM 8(9), 1965, 569.
.. [Dijkstra1968] Dijkstra, E.W. The structure of THE multiprogramming system. Comm. ACM 11(5), 1968, 341-346.
