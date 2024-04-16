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

from enum import Enum
from adhoccomputing.Experimentation.Topology import Topology
from adhoccomputing.GenericModel import GenericModel
from adhoccomputing.Generics import *
from time import sleep


class SharedExclusionMessageTypes(Enum):
    NONE = "SHARED_MESSAGE_NONE"
    LOCK = "SHARED_MESSAGE_LOCK"
    LOCK_ACK = "SHARED_MESSAGE_LOCK_ACK"
    ENTER = "SHARED_MESSAGE_ENTER"
    ENTER_ACK = "SHARED_MESSAGE_ENTER_ACK"
    UNLOCK = "SHARED_MESSAGE_UNLOCK"
    UNLOCK_ACK = "SHARED_MESSAGE_UNLOCK_ACK"


class SharedExclusionRequestTypes(Enum):
    NONE = "SHARED_REQUEST_NONE"
    LOCK = "SHARED_REQUEST_LOCK"
    ENTER = "SHARED_REQUEST_ENTER"
    UNLOCK = "SHARED_REQUEST_UNLOCK"


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
    NONE = 0
    UP = 1
    DOWN = 2
    PEER = 3


class SharedExclusionLock:
    """A generic lock implementation for mutual exclusion with support for processes with arbitrary positive pids."""

    def __init__(self, number_of_processes: int, no_op_duration: float):
        self.no_op_duration = no_op_duration
        self.number_of_processes: int = number_of_processes

        # A list of bools that marks which process indices are unused
        self.free_processes: list[bool] = [True] * number_of_processes

        # A dictionary of process id to process index
        self.process_dictionary: dict[int, int] = {}

    def addProcess(self, pid: int) -> int:
        """Adds a new process for arbitrary positive pid handling."""
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
        """Removes a process from arbitrary positive pid handling."""
        if pid not in self.process_dictionary.keys():
            return -1
        else:
            index = self.process_dictionary[pid]
            self.process_dictionary.pop(pid)
            self.free_processes[index] = True
            return index

    def getIndex(self, pid: int) -> int:
        """pid to internal index conversion."""
        if pid not in self.process_dictionary.keys():
            return -1
        else:
            return self.process_dictionary[pid]

    def getPID(self, index: int) -> int:
        """internal index to pid conversion."""
        if self.free_processes[index]:
            return -1
        else:
            for key in self.process_dictionary.keys():
                if self.process_dictionary[key] == index:
                    return key
            return -1

    def lock(self, pid: int):
        """Generic lock function, needs to be overloaded"""
        pass

    def unlock(self, pid: int):
        """Generic unlock function, needs to be overloaded"""
        pass

    def enter(self, pid: int):
        """Generic enter function, needs to be overloaded"""
        pass

    def no_op(self):
        sleep(self.no_op_duration)


class SharedExclusionMessageHeader(GenericMessageHeader):
    def __init__(self, messageType, messageFrom, messageTo, nextHop=float('inf'), interfaceID=float('inf'),
                 sequenceID=-1):
        super().__init__(messageType, messageFrom, messageTo, nextHop, interfaceID, sequenceID)


class SharedExclusionMessagePayload(GenericMessagePayload):
    def __init__(self,
                 originalsenderid,
                 originalreceiverid,
                 originalmessagetype,
                 originalsenderclock,
                 originalreceiverclock,
                 messagepayload=None):
        super().__init__(messagepayload)
        self.originalsenderid = originalsenderid
        self.originalreceiverid = originalreceiverid
        self.originalmessagetype = originalmessagetype
        self.originalsenderclock = originalsenderclock
        self.originalreceiverclock = originalreceiverclock


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

        self.otherNodeIDs = set()
        self.active_requests: dict[int, SharedExclusionRequest] = {}

    def on_init(self, eventobj: Event):
        self.otherNodeIDs = set(self.topology.nodes.keys())
        self.otherNodeIDs.remove(self.componentinstancenumber)

    def on_message_from_bottom(self, eventobj: Event):
        """
        Records the direction of the message and sends the generic message processing function
        """
        message = eventobj.eventcontent
        header = message.header
        self.message_received(Direction.DOWN, header, message)

    def on_message_from_top(self, eventobj: Event):
        """
        Records the direction of the message and sends the generic message processing function
        """
        message = eventobj.eventcontent
        header = message.header
        self.message_received(Direction.UP, header, message)

    def on_message_from_peer(self, eventobj: Event):
        """
        Records the direction of the message and sends the generic message processing function
        """
        message = eventobj.eventcontent
        header = message.header
        self.message_received(Direction.PEER, header, message)

    def message_received(self, direction: Direction, header, message):
        """
        Generic message processing function, forwards the message to the function that is supposed to
         process it according to its type
        """
        if header.messagetype == SharedExclusionMessageTypes.LOCK:
            self.lock_message(direction, header, message)
        elif header.messagetype == SharedExclusionMessageTypes.LOCK_ACK:
            self.lock_ack_message(direction, header, message)
        elif header.messagetype == SharedExclusionMessageTypes.ENTER:
            self.enter_message(direction, header, message)
        elif header.messagetype == SharedExclusionMessageTypes.ENTER_ACK:
            self.enter_ack_message(direction, header, message)
        elif header.messagetype == SharedExclusionMessageTypes.UNLOCK:
            self.unlock_message(direction, header, message)
        elif header.messagetype == SharedExclusionMessageTypes.UNLOCK_ACK:
            self.unlock_ack_message(direction, header, message)

    def lock_message(self, direction: Direction, header, message):
        """
        Generic behavior when a lock message is received, needs to be overloaded.
        """
        pass

    def lock_ack_message(self, direction: Direction, header, message):
        """
        Generic behavior when a lock acknowledgement message is received, needs to be overloaded.
        """
        pass

    def enter_message(self, direction: Direction, header, message):
        """
        Generic behavior when an enter message is received, needs to be overloaded.
        """
        pass

    def enter_ack_message(self, direction: Direction, header, message):
        """
        Generic behavior when an enter acknowledgement message is received, needs to be overloaded.
        """
        pass

    def unlock_message(self, direction: Direction, header, message):
        """
        Generic behavior when an unlock message is received, needs to be overloaded.
        """
        pass

    def unlock_ack_message(self, direction: Direction, header, message):
        """
        Generic behavior when an unlock acknowledgement message is received, needs to be overloaded.
        """
        pass

    def enter_critical_section(self):
        """
        Procedure to perform when the process needs to enter the critical section, need to be overloaded
        """
        pass

    def exit_critical_section(self):
        """
        Procedure to perform when the process needs to exit the critical section, need to be overloaded
        """
        pass

    def send_message(self, direction: Direction, message):
        """
        Sends a message in the specified direction
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
        nextHop = self.topology.get_next_hop(self.componentinstancenumber, targetId)
        interfaceID = f"{self.componentinstancenumber}-{nextHop}"
        header = SharedExclusionMessageHeader(messageType, self.componentinstancenumber, targetId, nextHop, interfaceID)
        message = GenericMessage(header, payload)
        if direction != Direction.NONE:
            self.send_message(direction, message)

    def relay_message(self, direction: Direction, header, message):
        nextHop = self.topology.get_next_hop(self.componentinstancenumber, header.messageto)
        interfaceID = f"{self.componentinstancenumber}-{nextHop}"
        if nextHop != float("inf") and nextHop != self.componentinstancenumber:
            header.nexthop = nextHop
            header.interfaceid = interfaceID
            message.header = header
            if direction != Direction.NONE:
                self.send_message(direction, message)

    def send_all(self, nodeID, messageType, payload):
        """
        Send the payload to all possible connections
        """
        self.send_message_to(nodeID, messageType, payload, Direction.UP)
        self.send_message_to(nodeID, messageType, payload, Direction.DOWN)
        self.send_message_to(nodeID, messageType, payload, Direction.PEER)

    def add_request(self, request_type, request_complete):
        clock = self.clock
        self.active_requests[clock] = SharedExclusionRequest(clock, request_type, len(self.otherNodeIDs),
                                                                  request_complete)
        self.clock += 1
        return clock
