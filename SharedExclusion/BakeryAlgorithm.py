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

from adhoccomputing.Experimentation.Topology import Topology
from adhoccomputing.GenericModel import GenericModel, GenericMessageHeader, GenericMessagePayload, GenericMessage
from adhoccomputing.Generics import *
from SharedExclusion.SharedExclusion import SharedExclusionComponentModel, SharedExclusionLock


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

        for i in range(self.number_of_processes):
            if not self.free_processes[i]:
                while self.entering[i]:
                    self.no_op()
                while (self.ticket[i] != 0 and
                       (self.ticket[i] < self.ticket[index] or (self.ticket[i] == self.ticket[index] and i < index))):
                    self.no_op()

    def unlock(self, pid: int):
        """Unlock function for Bakery Algorithm"""
        index = self.getIndex(pid)
        if index < 0:
            return
        self.ticket[index] = 0


class BakeryAlgorithmComponentModel(SharedExclusionComponentModel):
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
