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

from adhoccomputing.Experimentation.Topology import Topology
from adhoccomputing.GenericModel import GenericModel, GenericMessageHeader, GenericMessagePayload, GenericMessage
from adhoccomputing.Generics import *
from SharedExclusion.SharedExclusion import SharedExclusionComponentModel, SharedExclusionLock


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
        while self.waiting[(index - 1) % 2] and self.turn == (1 - index) % 2:
            self.no_op()

    def unlock(self, pid: int):
        """Unlock function for Peterson's Algorithm"""
        index = self.getIndex(pid)
        if index < 0:
            return
        self.waiting[index] = False


class PetersonsAlgorithmComponentModel(SharedExclusionComponentModel):
    def __init__(self, componentname, componentinstancenumber, context=None, configurationparameters=None, num_worker_threads=1, topology=None):
        super().__init__(componentname, componentinstancenumber, context, configurationparameters, num_worker_threads, topology)
        self.lock: PetersonsLock | None = None

    def on_init(self, eventobj: Event):
        super().on_init(eventobj)
        self.lock = PetersonsLock(self.no_op_duration)
        network_list = sorted(list(self.otherNodeIDs) + [self.componentinstancenumber])
        for net_member in network_list:
            self.lock.addProcess(net_member)

