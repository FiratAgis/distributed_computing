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
from adhoccomputing.GenericModel import GenericModel, GenericMessageHeader, GenericMessagePayload, GenericMessage
from adhoccomputing.Generics import *
from time import sleep


class SharedExclusionLock:
    """A generic lock implementation for mutual exclusion with support for processes with arbitrary positive pids."""
    def __init__(self, number_of_processes: int, no_op_duration: float):
        self.no_op_duration = no_op_duration
        self.number_of_processes: int = number_of_processes
        self.free_processes: list[bool] = [True] * number_of_processes  # A list of bools that marks which process indices are unused
        self.process_dictionary: dict[int, int] = {}  # A dictionary of process id to process index

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
        """Generic lock function"""
        pass

    def unlock(self, pid: int):
        """Generic unlock function"""
        pass

    def no_op(self):
        sleep(self.no_op_duration)


class SharedExclusionComponentModel(GenericModel):
    """
    A generic shared exclusion component model to implement various mutual exclusion algorithms.

    Extend SharedExclusionComponentModel to implement your own mutual exclusion algorithm.
    """
    no_op_duration = 1.0
    def __init__(self, componentname, componentinstancenumber, context=None, configurationparameters=None, num_worker_threads=1, topology=None):
        """
        Initializes the SharedExclusionComponentModel
        """
        super().__init__(componentname, componentinstancenumber, context, configurationparameters, num_worker_threads, topology)

        self.clock = 0

        self.otherNodeIDs = set()

        self.sentRequestCount = 0
        self.sentReplyCount = 0
        self.receivedRequestCount = 0
        self.receivedReplyCount = 0

    def on_init(self, eventobj: Event):
        self.otherNodeIDs = set(self.topology.nodes.keys())
        self.otherNodeIDs.remove(self.componentinstancenumber)
