# Global parameters (restructure the naming of variables if needed)
from modules import *
from graph import *


z0 = 0.3
z1 = 0.3

n = 10

nodes = range(n)  # list of all node ids
slow_nodes = np.random.choice(nodes, int(z0*n), replace=False) # list of slow node ids
low_cpu_nodes = np.random.choice(nodes, int(z1*n), replace=False) # list of low cpu power node ids
node_speeds = {i: NetworkSpeed.SLOW if i in slow_nodes else NetworkSpeed.FAST for i in nodes} # dictionary mapping node id to network speed
node_cpus = {i: CPUType.LOW if i in low_cpu_nodes else CPUType.HIGH for i in nodes} # dictionary mapping node id to cpu type

graph = make_connected_graph(n, seed=42, node_speeds=node_speeds, node_cpus=node_cpus) # generate connected graph with given number of nodes
for nid, node in graph.items():
    all_nodes[nid].neighbors = node.neighbors # assign neighbors to each node

# set hashing power, high cpu hash 10 and low cpu hash 1 then normalise
total_hash_power = sum(node.hash_power for node in all_nodes.values())

for node in all_nodes.values():
    node.hash_power /= total_hash_power
# for nid, node in all_nodes.items():
#     print(f"Node {nid} ({len(node.neighbors)} neighbors), Network speed: {node.network_speed.name}, CPU type: {node.cpu_type.name}")

current_time = 0.0
# simulator.timeout = 100  # set simulation timeout to 100 seconds
simulator.initialize_event_queue()

for node in all_nodes.values():
    print(f"Node {node.id} neighbors: {node.neighbors}")

while simulator.event_queue:
    event = heapq.heappop(simulator.event_queue)
    simulator.handle_event(event)
    time = event.time
    # print(event)

for node in all_nodes.values():
    print(f"Node {node.id}: Longest chain length = {node.blockchain.longest_chain_length}, Head = {node.blockchain.longest_chain_head[:3]}")
    print(node.blockchain)