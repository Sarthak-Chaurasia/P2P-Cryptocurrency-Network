from modules import *
from graph import *

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

current_time = 0.0
simulator.initialize_event_queue()

# to show the graph of the peers
# for node in all_nodes.values():
    # print(f"Node {node.id} neighbors: {node.neighbors}")

while simulator.event_queue:
    event = heapq.heappop(simulator.event_queue)
    simulator.current_time = event.time
    simulator.handle_event(event)

for node in all_nodes.values():
    node.blockchain.sync_longest_chain()
    # print(node.id,"\n",node.blockchain,"\n") # to show tree 

simulator._post_run(None, None)

# to make json of block arrival times at each node
# json_allnode_block_arrival()

# to visualize the blockchain tree of a particular node
# node = all_nodes[5]
# node.blockchain.draw_blockchain_tree()

# to print the orphan pool size of each node to ensure no orphans remain at the end of simulation
# print(len(node.blockchain.orphan_block_pool.keys()))