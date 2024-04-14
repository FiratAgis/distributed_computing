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


from SharedExclusion import SharedExclusionComponentModel, SharedExclusionLock


class BakeryLock(SharedExclusionLock):
    def __init__(self, number_of_processes: int, no_op_duration: float = 1.0):
        super().__init__(number_of_processes)
        self.entering: list[bool] = [False] * number_of_processes
        self.ticket: list[int] = [0] * number_of_processes

    def lock(self, pid: int):
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
                while self.ticket[i] != 0 and (self.ticket[i] < self.ticket[index] or (self.ticket[i] == self.ticket[index] and i < index)):
                    self.no_op()

    def unlock(self, pid: int):
        index = self.getIndex(pid)
        if index < 0:
            return
        self.ticket[index] = 0


class BakeryAlgorithmComponentModel(SharedExclusionComponentModel):
    def __init__(self, componentname, componentinstancenumber, context=None, configurationparameters=None, num_worker_threads=1, topology=None):
        super().__init__(componentname, componentinstancenumber, context, configurationparameters, num_worker_threads, topology)
