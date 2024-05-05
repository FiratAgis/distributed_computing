# SharedExclusion

## Usage

SharedExclusion implements two mutual exclusion algorithms, Peterson's Algorithm and Bakery Algorithm. They are both built on the same infrastructure, only differing in terms of the lock being used to regulate mutual exclusion in question. With the limitation that Peterson's Algorithm only supports two processes on the topology, their usage is identical.

1. Create each component, with each component's componentinstancenumber being a non-negative integer, and with am accurate topology.
2. Call set_leader for all components with the componentinstancenumber of the leader component that is responsible for maintaining the registers necessary for the algorithms work and managing in which order the processes enter the critical section.
3. Call set_callback for all components, assigning the fuction that will be run it is given permision to enter the critical section.
4. Send initialization event (Generics.EventTypes.INIT) to all components.
5. When a process wish to enter the critical section, it should call the enter_critical_section function of its corrosponding process, which will call the function assigned at step 2 when the permision is given.
6. After a process finishes its work in the critical section, it should call the exit_critical_section function of its corrosponding process.

