"""
    Implementation of the Peterson's Algorithm for mutual exclusion.
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

from adhoccomputing.Generics import *
from SharedExclusion.SharedExclusion import SharedExclusionComponentModel, SharedExclusionLock, \
    SharedExclusionMessagePayload, SharedExclusionMessageHeader, SharedExclusionMessageTypes, Direction


class PetersonsLock(SharedExclusionLock):
    def __init__(self, no_op_duration: float = 1.0):
        super().__init__(2, no_op_duration)
        self.waiting = [False] * 2
        self.turn = 0

    def lock(self, pid: int):
        """Lock function for Peterson's Algorithm"""
        index = self.getIndex(pid)
        if index < 0:
            return
        self.waiting[index] = True
        self.turn = (1 - index) % 2

    def unlock(self, pid: int):
        """Unlock function for Peterson's Algorithm"""
        index = self.getIndex(pid)
        if index < 0:
            return
        self.waiting[index] = False

    def enter(self, pid: int):
        """Enter function for Peterson's Algorithm"""
        index = self.getIndex(pid)
        if index < 0:
            return
        if self.waiting[(index - 1) % 2] and self.turn == (1 - index) % 2:
            self.no_op()


class PetersonsAlgorithmMessageHeader(SharedExclusionMessageHeader):
    def __init__(self, messageType, messageFrom, messageTo, nextHop=float('inf'), interfaceID=float('inf'),
                 sequenceID=-1):
        super().__init__(messageType, messageFrom, messageTo, nextHop, interfaceID, sequenceID)


class PetersonsAlgorithmMessagePayload(SharedExclusionMessagePayload):
    def __init__(self, messagepayload=None):
        super().__init__(messagepayload)


class PetersonsAlgorithmComponentModel(SharedExclusionComponentModel):
    """
    Component for managing the Shared Memory Mutual Exclusion via Peterson's Algorithm
    """
    def __init__(self,
                 componentname,
                 componentinstancenumber,
                 context=None,
                 configurationparameters=None,
                 num_worker_threads=1,
                 topology=None):
        super().__init__(componentname, componentinstancenumber, context, configurationparameters, num_worker_threads,
                         topology)
        self.lock: PetersonsLock | None = None

    def on_init(self, eventobj: Event):
        """
        After calling the parent on_init, initializes the self.lock: PetersonsLock and adds the members of the topology
        to it.
        """
        super().on_init(eventobj)
        self.lock = PetersonsLock(self.no_op_duration)
        network_list = sorted(list(self.otherNodeIDs) + [self.componentinstancenumber])
        for net_member in network_list:
            self.lock.addProcess(net_member)

    def message_received(self, direction: Direction, header, message):
        """
        If the message is for the component, calls the parent function for redirecting it to the correct function. If
        the message is not for the component, calls the function for relaying the message.
        """
        if header.messageto != self.componentinstancenumber:
            if header.nexthop == self.componentinstancenumber:
                self.relay_message(direction, header, message)
        elif header.messagetype in SharedExclusionMessageTypes:
            super().message_received(direction, header, message)

    def request_message(self, direction: Direction, header: PetersonsAlgorithmMessageHeader, message):
        """
        If the component is the leader, performs the appropriate actions necessary when a process requests entry
        into the critical section.
        """
        if self.componentinstancenumber == self.leaderId:
            self.lock.lock(header.messagefrom)
            self.lock.enter(header.messagefrom)
            self.send_message_to(header.messagefrom, SharedExclusionMessageTypes.ENTER_PERMISSION, None, direction)

    def permission_message(self, direction: Direction, header, message):
        """
        Calls the callback function (the function that will use the critical section). If callback function is not set,
        automatically exits the critical section. Otherwise, after the function is done with the critical section, it
        should call the exit_critical_section function.
        """
        if self.callback is not None:
            self.callback()
        else:
            self.exit_critical_section()

    def notification_message(self, direction: Direction, header, message):
        """
        If the component is the leader, performs the appropriate actions necessary when a process requests to exit
        from the critical section.
        """
        if self.componentinstancenumber == self.leaderId:
            self.lock.unlock(header.messagefrom)
