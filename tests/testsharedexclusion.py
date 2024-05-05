import time

from adhoccomputing.Generics import *
from adhoccomputing.Experimentation.Topology import Topology
from adhoccomputing.Networking.LogicalChannels.GenericChannel import GenericChannel

import networkx as nx

from SharedExclusion.BakeryAlgorithm import BakeryAlgorithmComponentModel
from SharedExclusion.SharedExclusion import SharedExclusionMessageTypes


def callback():
    print(f"Entered Critical Section")
    time.sleep(1)
    print(f"Exited Critical Section")


def main():
    setAHCLogLevel(DEBUG)
    topo = Topology()
    graph = nx.Graph()
    graph.add_nodes_from(list(range(0, 10)))

    for first_val in range(0, 10):
        for second_val in range(first_val + 1, 10):
            graph.add_edge(first_val, second_val)

    topo.construct_from_graph(graph, BakeryAlgorithmComponentModel, GenericChannel)
    # A larger topology is required for testing

    for i in topo.nodes:
        topo.nodes[i].set_leader(0)
        topo.nodes[i].set_callback(callback)

    topo.start()
    time.sleep(1)

    for i in topo.nodes:
        topo.nodes[i].enter_critical_section()
        time.sleep(5)
        topo.nodes[i].exit_critical_section()
    time.sleep(5)
    topo.exit()


if __name__ == "__main__":
    exit(main())