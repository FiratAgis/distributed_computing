.. include:: substitutions.rst

SharedExclusion
=========================================

In a regular systems with multiple processes or a disturbuted systems with many members (which we will also call processes for simplicity), while working on the same data, it is common for many processes to want to access or modify the same piece of data. But a process changing the data while the other is reading it might create unwanted effects. We call these race conditions, where two or more processes races to work on the same piece of memory. We call the regions of code that access or modify the same shared memory a critical section. Mutual exclusion in a shared memory is a common way of handling these race conditions, by forcing processes to enter critical sections in a mutually exclusive fashion. This enables multiple processes to work on the same piece of data, which enables us to run algorithms which process a piece of data in a concurent way.

Background and Related Work
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Present any background information survey the related work. Provide citations.

Distributed Algorithm: SharedExclusion
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

SharedExclusion is a collection of algorithms for mutual exclusion in shared distrubuted memory, spesifically Peterson's :ref:`Algorithm <PetersonsAlgorithm>` [Peterson1981]_ and Bakery :ref:`Algorithm <BakeryAlgorithm>` [Lamport1974]_.  


Peterson's Algorithm
""""""""""""""""""""""""

Peterson's :ref:`Algorithm <PetersonsAlgorithm>` [Peterson1981]_ works for 2 processes, lets call them p_0 and p_1, and prevents both of them from entering the critical section in the same time. It achives this by a way of each process giving way to other. When the process comes to the critical section, it first allows the other process to continue to the critical section and only moves forward if the other is not currently trying to enter the critical section or if the other process finishes its work within the critical section. While it is a gentlemen's way of handling shared memory exclusion, its main limitation lies in the fact that it only works for 2 processes. This can be circumnavigated by a cascading giving way action for processes arranged in a binary tree but that will be explored later.

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

While many idea of the algorithm is simple, it is benefical to get a line by line perspective.

* In line 1 two variables are initilized, turn and waiting.

    * turn is a boolean, or more precisely a binary integer as it is used in the algorithm, that determines which processes turn it is to enter the critical section. When turn = 0, it is p_0's turn and vice versa.
    * waiting is a boolean array with length 2 that determines if a process is waiting to enter the critical section or not. 

* In line 3, it is checked that if a process wants to enter the critical section. If not, no action needs to be taken.
* In line 4, the process establishes that it is waiting to enter the critical section
* In line 5, the process gives way to the other process.
* In lines 7-8, the process waits until either it is its turn to enter the critical section, or the other process does not have any intention of entering the critical section at the time. When either one of this consitions are met, it proceeds.
* In lines 10-12, the process does whatever it needs to do in the critical section.
* In line 14, the process establishes that its work with the critical section is done and it is no longer waiting to access the critical section.

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
			
            ticket[i] = 0;
			
        end if
		
The slight complexity of the algorithm when compared with the Peterson's :ref:`Algorithm <PetersonsAlgorithm>`, which enables the Bakery Algorithm to serve any number of processes (n processes, identified by p_i, i in [1, n]), warrants a closer examination of the psuedocode.

* In line 1, entering is initilized. It is a boolean array with length n. It determines whether a process is trying to get a ticket at that timeframe or not.
* In line 2, tickes is initilized. It is a integer array with length n. It determines the number on a process' ticket.
* In line 4, it is checked that if a process wants to enter the critical section. If not, no action needs to be taken.
* In lines 5-7, the process takes a ticket whose number comes after all processes that are currently waiting to enter the critical section, as it arrived later then them.
* In lines 9-14, the process waits,

    * if any process is currently trying to get a ticket, as tickets taken within close proximity of eachother might have the same number on them due to context switches between read and write operations (lines 10-11).
    * if any process with a lower number on its ticket or a more senior process with the same number on its ticket is also waiting to enter the critical section (lines 12-13).

* In lines 16-18, the process does whatever it needs to do in the critical section.
* In line 20, the processes get rid of its ticket, allowing processes with tickets containing greater numbers to also get into the critical section.

Example
~~~~~~~~

Provide an example for the distributed algorithm.

Correctness
~~~~~~~~~~~

Present Correctness, safety, liveness and fairness proofs.


Complexity 
~~~~~~~~~~

Present theoretic complexity results in terms of number of messages and computational complexity.


.. [Lamport1974] L. Lamport, A new solution of Dijkstra’s concurrent programming problem, Communications of the ACM, 17(8), 1974, 453–455.
.. [Peterson1977] G. L. Peterson and M. Fischer, Economical solutions for the mutual exclusion problem in a distributed system, Proceedings of the 9th ACM Symposium on Theory of Computing, 1977, 91–97.
.. [Peterson1981] G. L. Peterson, Myths about the mutual exclusion problem, Information Processing Letters, 12, 1981, 115–116.
