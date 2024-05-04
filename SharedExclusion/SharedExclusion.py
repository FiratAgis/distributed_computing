"""
    Implementation of a generic mutual exclusion component for implementing the Peterson's and Bakery Algorithms.
"""

__author__ = "Fırat Ağış"
__contact__ = "firat@ceng.metu.edu.tr"
__copyright__ = "Copyright 2024, WINSLAB"
__credits__ = ["Fırat Ağış"]
__date__ = "2024/04/14"
__deprecated__ = False
__email__ = "firat@ceng.metu.edu.tr"
__license__ = "GPLv3"
__maintainer__ = "developer"
__status__ = "Production"
__version__ = "0.0.1"

from adhoccomputing.Experimentation.Topology import Topology
from adhoccomputing.GenericModel import GenericModel
from adhoccomputing.Generics import *
from time import sleep


class SharedExclusionMessageTypes(Enum):
    """
    Message types for requesting entry to the critical section, granting permission to the critical section and
    notifying the exit from the critical section.
    """
    NONE = "SHARED_MESSAGE_NONE"
    ENTER_REQUEST = "SHARED_MESSAGE_ENTER_REQUEST"
    ENTER_PERMISSION = "SHARED_MESSAGE_ENTER_REQUEST"
    LEAVE_NOTIFICATION = "SHARED_LEAVE_NOTIFICATION"


class SharedExclusionRequest:
    def __init__(self, request_clock, request_type, request_count, request_complete):
        self.request_clock = request_clock
        self.request_type = request_type
        self.request_count = request_count
        self.request_complete = request_complete
        self.request_current = 0

    def add_to_current(self):
        self.request_current += 1
        if self.request_current >= self.request_count:
            self.request_complete(self)


class Direction(Enum):
    """
    Directions for the purpose of sending messages, enabling responding messages from the direction they came before.
    But newly generated messages assumes Direction.DOWN as the default direction.
    """
    NONE = 0
    UP = 1
    DOWN = 2
    PEER = 3


class SharedExclusionLock:
    """
    A generic lock implementation for mutual exclusion with support for processes with arbitrary positive pids.
    """

    def __init__(self, number_of_processes: int, no_op_duration: float):
        """
        Initializes the lock.

        Parameters
        -----------
        number_of_processes: int
            Number of processes the lock will be responsible for.
        no_op_duration: float
            The duration of sleep when the no-op operation is called, in terms of seconds.
        """
        self.no_op_duration = no_op_duration
        self.number_of_processes: int = number_of_processes

        # A list of bools that marks which process indices are unused
        self.free_processes: list[bool] = [True] * number_of_processes

        # A dictionary of process id to process index
        self.process_dictionary: dict[int, int] = {}

    def addProcess(self, pid: int) -> int:
        """
        Adds a new process for arbitrary positive pid handling.

        Parameters
        -----------
        pid: int
            Process id of a process.

        Returns
        --------
        int
            Returns the index of the process. Returns -1 if all possible indices are taken.
        """
        retval = 0
        while retval < self.number_of_processes and (not self.free_processes[retval]):
            retval += 1
        if retval < self.number_of_processes:
            self.process_dictionary[pid] = retval
            self.free_processes[retval] = False
            return retval
        else:
            return -1

    def removeProcess(self, pid: int) -> int:
        """
        Removes a process from arbitrary positive pid handling.

        Parameters
        -----------
        pid: int
            Process id of a process.

        Returns
        --------
        int
            Returns the freed index. Returns -1 if the process was not handled by the lock.
        """
        if pid not in self.process_dictionary.keys():
            return -1
        else:
            index = self.process_dictionary[pid]
            self.process_dictionary.pop(pid)
            self.free_processes[index] = True
            return index

    def getIndex(self, pid: int) -> int:
        """
        Process id to internal index conversion.

        Parameters
        -----------
        pid: int
            Process id of a process.

        Returns
        --------
        int
            Current index of the process. Returns -1 if the process was not handled by the lock.
        """
        if pid not in self.process_dictionary.keys():
            return -1
        else:
            return self.process_dictionary[pid]

    def getPID(self, index: int) -> int:
        """
        Internal index to process id conversion.

        Parameters
        -----------
        index: int
            Internal index of a process.

        Returns
        --------
        int
            Process id of the process with the given index. Returns -1 if the index is free.
        """
        if self.free_processes[index]:
            return -1
        else:
            for key in self.process_dictionary.keys():
                if self.process_dictionary[key] == index:
                    return key
            return -1

    def lock(self, pid: int):
        """
        Generic lock function, needs to be overloaded.

        Parameters
        -----------
        pid: int
            Process id of a process.
        """
        pass

    def unlock(self, pid: int):
        """
        Generic unlock function, needs to be overloaded.

        Parameters
        -----------
        pid: int
            Process id of a process.
        """
        pass

    def enter(self, pid: int):
        """
        Generic enter function, needs to be overloaded.

        Parameters
        -----------
        pid: int
            Process id of a process.
        """
        pass

    def no_op(self):
        """
        NO-OP operation, calls sleep for a predetermined amount of time.
        """
        sleep(self.no_op_duration)


class SharedExclusionMessageHeader(GenericMessageHeader):
    def __init__(self, messageType, messageFrom, messageTo, nextHop=float('inf'), interfaceID=float('inf'),
                 sequenceID=-1):
        super().__init__(messageType, messageFrom, messageTo, nextHop, interfaceID, sequenceID)


class SharedExclusionMessagePayload(GenericMessagePayload):
    def __init__(self, payload):
        super().__init__(payload)


class SharedExclusionComponentModel(GenericModel):
    """
    A generic shared exclusion component model to implement various mutual exclusion algorithms.

    Extend SharedExclusionComponentModel to implement your own mutual exclusion algorithm.
    """
    no_op_duration = 1.0

    def __init__(self,
                 componentname,
                 componentinstancenumber,
                 context=None,
                 configurationparameters=None,
                 num_worker_threads=1,
                 topology=None):
        """
        Initializes the SharedExclusionComponentModel
        """
        super().__init__(componentname, componentinstancenumber, context, configurationparameters, num_worker_threads,
                         topology)

        self.clock = 0
        self.leaderId = 0
        self.otherNodeIDs = set()
        self.callback = None

    def on_init(self, eventobj: Event):
        """
        Collects the other members of the topology on initialization.
        """
        self.otherNodeIDs = set(self.topology.nodes.keys())
        self.otherNodeIDs.remove(self.componentinstancenumber)

    def set_leader(self, leaderId: int):
        """
        Set the leader of the group, should be called by a component that does leader election for every member of
        the topology before initialization.
        """
        self.leaderId = leaderId

    def set_callback(self, callback):
        """
        Sets the action that will be performed when the process enters the critical section. Can potentially be changed
        in runtime.
        """
        self.callback = callback

    def on_message_from_bottom(self, eventobj: Event):
        """
        Records the direction of the message and sends the generic message processing function.
        """
        message = eventobj.eventcontent
        header = message.header
        self.message_received(Direction.DOWN, header, message)

    def on_message_from_top(self, eventobj: Event):
        """
        Records the direction of the message and sends the generic message processing function.
        """
        message = eventobj.eventcontent
        header = message.header
        self.message_received(Direction.UP, header, message)

    def on_message_from_peer(self, eventobj: Event):
        """
        Records the direction of the message and sends the generic message processing function.
        """
        message = eventobj.eventcontent
        header = message.header
        self.message_received(Direction.PEER, header, message)

    def message_received(self, direction: Direction, header, message):
        """
        Generic message processing function, forwards the message to the function that is supposed to
        process it according to its type.
        """
        if header.messagetype == SharedExclusionMessageTypes.ENTER_PERMISSION:
            self.permission_message(direction, header, message)
        elif header.messagetype == SharedExclusionMessageTypes.ENTER_REQUEST:
            self.request_message(direction, header, message)
        elif header.messagetype == SharedExclusionMessageTypes.LEAVE_NOTIFICATION:
            self.notification_message(direction, header, message)

    def permission_message(self, direction: Direction, header, message):
        """
        Procedure to perform when the messages that gives the process permission to enter the critical section
        arrives, need to be overloaded.
        """
        pass

    def request_message(self, direction: Direction, header, message):
        """
        Procedure to perform when the messages that ask for a process permission to enter the critical section
        arrives, need to be overloaded. Should only be applicable to the leader of the group.
        """
        pass

    def notification_message(self, direction: Direction, header, message):
        """
        Procedure to perform when the messages that notifies the leader that a process exited the critical section
        arrives, need to be overloaded. Should only be applicable to the leader of the group.
        """
        pass

    def enter_critical_section(self):
        """
        Procedure to perform when the process needs to enter the critical section, sends a request to the leader for
        entering the critical section.
        """
        self.send_message_to(self.leaderId, SharedExclusionMessageTypes.ENTER_REQUEST, None, Direction.DOWN)

    def exit_critical_section(self):
        """
        Procedure to perform when the process needs to exit the critical section, sends a notification the leader that
        the procudure is done with the critical section.
        """
        self.send_message_to(self.leaderId, SharedExclusionMessageTypes.LEAVE_NOTIFICATION, None, Direction.DOWN)

    def send_message(self, direction: Direction, message):
        """
        Sends a message in the specified direction.
        """
        if direction == Direction.NONE:
            self.send_self(Event(self, ))
        if direction == Direction.UP:
            self.send_up(Event(self, EventTypes.MFRB, message))
        if direction == Direction.DOWN:
            self.send_down(Event(self, EventTypes.MFRT, message))
        if direction == Direction.PEER:
            self.send_up(Event(self, EventTypes.MFRP, message))

    def send_message_to(self, targetId, messageType, payload, direction: Direction = Direction.NONE):
        """
        Default function for sending messages.
        """
        nextHop = self.topology.get_next_hop(self.componentinstancenumber, targetId)
        interfaceID = f"{self.componentinstancenumber}-{nextHop}"
        header = SharedExclusionMessageHeader(messageType, self.componentinstancenumber, targetId, nextHop, interfaceID)
        message = GenericMessage(header, payload)
        if direction != Direction.NONE:
            self.send_message(direction, message)

    def relay_message(self, direction: Direction, header, message):
        """
        Default function for relaying messages.
        """
        nextHop = self.topology.get_next_hop(self.componentinstancenumber, header.messageto)
        interfaceID = f"{self.componentinstancenumber}-{nextHop}"
        if nextHop != float("inf") and nextHop != self.componentinstancenumber:
            header.nexthop = nextHop
            header.interfaceid = interfaceID
            message.header = header
            if direction != Direction.NONE:
                self.send_message(direction, message)
