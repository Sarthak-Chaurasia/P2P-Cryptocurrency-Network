# Global parameters (restructure the naming of variables if needed)
from modules import *
from graph import make_connected_graph
from events import Event, EventTypes
from nodes import NetworkSpeed, CPUType, all_nodes

n: int  # number of nodes
z0: float # ratio of slow nodes
z1: float # ratio of low CPU power nodes
T_tx: float # inter arrival time between transactions
T_interarrival: float # inter arrival time between blocks
timeout = None # timeout for simulation, None for our purposes, we end simulation with SigInt
visualize: bool # enable visualization

## Constants


# Network speeds in Mbps
c_fast: int = 100
c_slow: int = 5
d_const: float = 96e-3

# Speed of light in s
rho_min: float = 10e-3
rho_max: float = 500e-3

# Transaction and block sizes in Mb
tx_size: float = 8e-3
block_max_size: int = 8

# Reward and initial balance in coins
init_balance: int = 0
reward: int = 50

# Number of neighbors
n_low: int = 3
n_high: int = 6

# Hash power multiplier
hash_power_mult: int = 10

def sha256(data):
    return hashlib.sha256(data.encode()).hexdigest()

def random_val():
    return np.random.uniform(0, 1)

def exp_random_val():
    return np.random.exponential(1)

class Simulator:
    def __init__(self):
        self.event_queue = []
    
    def handle_event(self, event):
        if event.type == EventTypes.GENERATE_TXN:
            txn = event.node.blockchain.generate_txn(event.node, event.data)
            self.event_queue.append(Event(event.time, EventTypes.PROPAGATE_TXN, event.node.id, txn))
        elif event.type == EventTypes.GENERATE_BLOCK:
            block, tk = event.node.blockchain.mine_block(event.node)
            self.event_queue.append(Event(event.time, EventTypes.PROPAGATE_BLOCK, event.node.id, block))
        elif event.type == EventTypes.PROPAGATE_TXN:
            for neighbor_id in event.node.neighbors:
                # delay = event.node.network_delay(all_nodes[neighbor_id], event.data.size)
                all_nodes[neighbor_id].capture_txn(event.data)
        elif event.type == EventTypes.PROPAGATE_BLOCK:
            for neighbor_id in event.node.neighbors:
                # delay = event.node.network_delay(all_nodes[neighbor_id], event.data.size)
                all_nodes[neighbor_id].capture_block(event.data)

    # def send_txn(self, event):
    #     print(f"Sending transaction event: {event}")
    #     all_nodes[event.node_id].mempool.append(event.data)
    #     for neighbor_id in all_nodes[event.node_id].neighbors:
    #         heapq.heappush(event_list, Event(event.time + all_nodes[event.node_id].network_delay(all_nodes[neighbor_id], event.data.size), EventTypes.RECEIVE_TXN, neighbor_id, event.data))

    # def receive_txn(self, event):
    #     if event.data in all_nodes[event.node_id].mempool:
    #         print("Duplicate transaction received, discarding")
    #         return  # Discard duplicate transaction
    #     print(f"Node {event.node_id} received transaction {event.data.id}")
    #     all_nodes[event.node_id].mempool.append(event.data)
    #     for neighbor_id in all_nodes[event.node_id].neighbors:
    #         heapq.heappush(event_list, Event(event.time + all_nodes[event.node_id].network_delay(all_nodes[neighbor_id], event.data.size), EventTypes.RECEIVE_TXN, neighbor_id, event.data))
            
    # def send_block(self, event):
    #     all_nodes[event.node_id].blockchain.append(event.data)
    #     print(f"Sending block event: {event}")
    #     for neighbor_id in all_nodes[event.node_id].neighbors:
    #         heapq.heappush(event_list, Event(event.time + all_nodes[event.node_id].network_delay(all_nodes[neighbor_id], event.data.size), EventTypes.RECEIVE_BLOCK, neighbor_id, event.data))

    # def receive_block(self, event):
    #     if event.data in all_nodes[event.node_id].blockchain:
    #         print("Duplicate block received, discarding")
    #         return  
        
    #     # check if is valid function should be in block or in node
    #     if all_nodes[event.node_id].is_block_valid(event.data):
    #         all_nodes[event.node_id].blockchain.append(event.data)
    #         for txn in event.data.transactions:
    #             if txn in all_nodes[event.node_id].mempool:
    #                 all_nodes[event.node_id].mempool.remove(txn)
                    
    #     print(f"Node {event.node_id} received block {event.data.id}")
    #     for neighbor_id in all_nodes[event.node_id].neighbors:
    #         heapq.heappush(event_list, Event(event.time + all_nodes[event.node_id].network_delay(all_nodes[neighbor_id], event.data.size), EventTypes.RECEIVE_BLOCK, neighbor_id, event.data))

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


simulator = Simulator()

while event_list:
    event = heapq.heappop(event_list)
    simulator.handle_event(event)
    time = event.time
    print(event.__str__())