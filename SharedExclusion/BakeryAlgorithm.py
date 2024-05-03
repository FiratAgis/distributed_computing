"""
    Implementation of the Bakery Algorithm for mutual exclusion.
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
    SharedExclusionMessagePayload, SharedExclusionMessageHeader, Direction, SharedExclusionMessageTypes


class BakeryLock(SharedExclusionLock):
    def __init__(self, number_of_processes: int, no_op_duration: float = 1.0):
        super().__init__(number_of_processes, no_op_duration)
        self.entering: list[bool] = [False] * number_of_processes
        self.ticket: list[int] = [0] * number_of_processes

    def lock(self, pid: int):
        """Lock function for Bakery Algorithm"""
        index = self.getIndex(pid)
        if index < 0:
            return
        self.entering[index] = True
        self.ticket[index] = max(self.ticket) + 1
        self.entering[index] = False

    def unlock(self, pid: int):
        """Unlock function for Bakery Algorithm"""
        index = self.getIndex(pid)
        if index < 0:
            return
        self.ticket[index] = 0
        self.isInside = False

    def enter(self, pid: int):
        """Enter function for Peterson's Algorithm"""
        index = self.getIndex(pid)
        if index < 0:
            return
        for i in range(self.number_of_processes):
            if not self.free_processes[i]:
                while self.entering[i]:
                    self.no_op()
                while (self.ticket[i] != 0 and
                       (self.ticket[i] < self.ticket[index] or (self.ticket[i] == self.ticket[index] and i < index))):
                    self.no_op()


class BakeryAlgorithmMessageHeader(SharedExclusionMessageHeader):
    def __init__(self, messageType, messageFrom, messageTo, nextHop=float('inf'), interfaceID=float('inf'),
                 sequenceID=-1):
        super().__init__(messageType, messageFrom, messageTo, nextHop, interfaceID, sequenceID)


class BakeryAlgorithmMessagePayload(SharedExclusionMessagePayload):
    def __init__(self,
                 messagepayload=None):
        super().__init__(messagepayload)


class BakeryAlgorithmComponentModel(SharedExclusionComponentModel):
    """
    Component for managing the Shared Memory Mutual Exclusion via Bakery Algorithm
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
        self.lock: BakeryLock | None = None

    def on_init(self, eventobj: Event):
        super().on_init(eventobj)
        self.lock = BakeryLock(len(self.otherNodeIDs) + 1, self.no_op_duration)
        network_list = sorted(list(self.otherNodeIDs) + [self.componentinstancenumber])
        for net_member in network_list:
            self.lock.addProcess(net_member)

    def message_received(self, direction: Direction, header, message):
        if header.messageto != self.componentinstancenumber:
            if header.nexthop == self.componentinstancenumber:
                self.relay_message(direction, header, message)
        elif header.messagetype in SharedExclusionMessageTypes:
            super().message_received(direction, header, message)

    def request_message(self, direction: Direction, header: BakeryAlgorithmMessageHeader, message):
        if self.componentinstancenumber == self.leaderId:
            self.lock.lock(header.messagefrom)
            self.lock.enter(header.messagefrom)
            self.send_message_to(header.messagefrom, SharedExclusionMessageTypes.ENTER_PERMISSION, None, direction)

    def permission_message(self, direction: Direction, header, message):
        self.enter_critical_section()
        self.exit_critical_section()
        self.send_message_to(self.leaderId, SharedExclusionMessageTypes.LEAVE_NOTIFICATION, None, direction)

    def notification_message(self, direction: Direction, header, message):
        if self.componentinstancenumber == self.leaderId:
            self.lock.unlock(header.messagefrom)

    def enter_critical_section(self):
        pass

    def exit_critical_section(self):
        pass
