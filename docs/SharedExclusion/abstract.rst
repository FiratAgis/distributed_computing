.. include:: substitutions.rst
========
Abstract
========

Mutual exclusion is the bedrock of shared memory. Without utilizing mutual exclusion, it is nearly impossible to have two or more processes accessing and modifying the same data without catastrophic failure. Many challenges exist in terms of applying mutual exclusion, maintaining consistency, and order being the mandatory requirements, with the addition of minimizing messages sent, memory used, and time spent stalling affecting the performance of the processes involved being goals to strive for. While achieving all of these at the same time is impossible, two of the oldest and thus most proven algorithms, Peterson's Algorithm and Bakery Algorithm, achieve our mandatory requirements with great usage of bandwidth and memory, with minimal computation. Their age and their lack of modern considerations make them not suitable for every single situation; their consistency and generalist nature make them useful in most situations. In this paper, we implemented both these algorithms on the AHCv2 platform and investigated their performance in terms of previously mentioned criteria in a wide range of situations.

