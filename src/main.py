# Global parameters (restructure the naming of variables if needed)
from modules import *
from graph import *


z0 = 0.3
z1 = 0.3
event_list = []

n=100


nodes = range(n)  # list of all node ids
slow_nodes = np.random.choice(nodes, int(z0*n), replace=False) # list of slow node ids
low_cpu_nodes = np.random.choice(nodes, int(z1*n), replace=False) # list of low cpu power node ids
node_speeds = {i: NetworkSpeed.SLOW if i in slow_nodes else NetworkSpeed.FAST for i in nodes} # dictionary mapping node id to network speed
node_cpus = {i: CPUType.LOW if i in low_cpu_nodes else CPUType.HIGH for i in nodes} # dictionary mapping node id to cpu type
# all_nodes = {i: Node(i, node_cpus[i], node_speeds[i]) for i in nodes} # dictionary mapping node id to Node object

graph = make_connected_graph(n, seed=42, node_speeds=node_speeds, node_cpus=node_cpus) # generate connected graph with given number of nodes
for nid, node in graph.items():
    all_nodes[nid].neighbors = node.neighbors # assign neighbors to each node

# set hashing power, high cpu hash 10 and low cpu hash 1 then normalise
total_hash_power = sum(node.hash_power for node in all_nodes.values())
for node in all_nodes.values():
    node.hash_power /= total_hash_power
    
print("Graph generated with the following nodes and their neighbors:")
for nid, node in all_nodes.items():
    print(f"Node {nid} ({len(node.neighbors)} neighbors), Network speed: {node.network_speed.name}, CPU type: {node.cpu_type.name}")

current_time = 0.0
for node in all_nodes.values():
    block, time = node.generate_block()
    heapq.heappush(event_list, Event(current_time + time, EventTypes.PROPAGATE_BLOCK, node.id, block))
    id = np.random.randint(0, n)
    while id != node.id:
        id = np.random.randint(0, n)
    txn = node.generate_txn(id)
    T_tx = 1 # random test value
    t0 = np.random.exponential(T_tx)
    event_time = current_time + t0
    heapq.heappush(event_list, Event(event_time, EventTypes.PROPAGATE_TXN, node.id, txn))


while event_list:
    event = heapq.heappop(event_list)
    simulator.handle_event(event)
    time = event.time
    print(event.__str__())