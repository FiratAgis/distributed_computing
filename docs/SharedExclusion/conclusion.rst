.. include:: substitutions.rst

Conclusion
==========

While in a diminished capacity, I implemented working mutual exclusion algorithms for the AHCv2 platform as well as a general framework for future implementations of centralized mutual exclusion algorithms. Due to the limitations of both the algorithms and my implementations of them, I was unable to produce significant experimental results.


Future Work
~~~~~~~~~~~~

There are many improvements I can see implemented in the future. 

1. For better integration with the event-driven nature of the AHCv2 ecosystem and more flexible usage, leader assignment,
    * can be done via messages,
    * can be done after initialization, 
    * ideally, should be able to change during runtime.
2. Also, for better integration and flexibility, other components should be able to ask the SharedExclusion components to manage their access to the critical section via messages instead of assigning callback functions.
3. Extending Peterson's Algorithm in a binary tree-like structure could allow it to handle multiple processes in exchange for possible performance loss. This implementation can also be compared with the Bakery Algorithm more fairly.
4. Leader-reliant implementation can be shifted to work in a truly distributed system by following the original papers' implementations more closely.