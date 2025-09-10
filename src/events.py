from modules import *

# All events that are scheduled need to be defined here
class EventTypes(Enum):
    GENERATE_TXN = "generate a new transaction on node and add propagate to event queue"
    GENERATE_BLOCK = "generate a new block on node and add propagate to event queue"
    PROPAGATE_TXN = "propagate txn to neighbors of node"
    PROPAGATE_BLOCK = "propagate block to neighbors of node"

# Event class; event queue will be a global priority queue, not node specific
class Event:
    def __init__(self, time, event_type, node_id, data=None):
        self.time = time
        self.event_type = event_type
        self.node_id = node_id  # the node on which the event occurs
        self.data = data
    
    def __lt__(self, other):
        return self.time < other.time
    
    def __str__(self):
        return f"Time {self.time:.5f}: Node {self.node_id} {self.event_type.value}"
    
class Simulator:
    def __init__(self,timeout=float('inf')):
        self.event_queue = []
        self.timeout = timeout              # simulation timeout; set as None for now so need to Ctrl+C to end simulation
        self.start_time = time.time()
        self.current_time = 0.0

        signal.signal(signal.SIGINT, self._post_run)
    
    def handle_event(self, event):
        if time.time() - self.start_time > self.timeout:
            self._post_run(None, None)
        if event.event_type == EventTypes.GENERATE_TXN:
            txn = all_nodes[event.node_id].blockchain.generate_txn(all_nodes[event.node_id], event.data)
            # print(txn)
            for neighbor_id in all_nodes[event.node_id].neighbors:
                delay = all_nodes[event.node_id].network_delay(all_nodes[neighbor_id], tx_size)
                heapq.heappush(self.event_queue, Event(simulator.current_time + delay, EventTypes.PROPAGATE_TXN, neighbor_id, {"dest": neighbor_id, "trxn": txn}))
            # heapq.heappush(self.event_queue, Event(0, EventTypes.PROPAGATE_TXN, event.node_id, txn))
        elif event.event_type == EventTypes.GENERATE_BLOCK:
            block = all_nodes[event.node_id].blockchain.mine_block(all_nodes[event.node_id])
            # print(block)
            for neighbor_id in all_nodes[event.node_id].neighbors:
                delay = all_nodes[event.node_id].network_delay(all_nodes[neighbor_id], block.size)
                heapq.heappush(self.event_queue, Event(simulator.current_time + delay, EventTypes.PROPAGATE_BLOCK, neighbor_id, {"dest": neighbor_id, "block": block}))
            # heapq.heappush(self.event_queue, Event(0, EventTypes.PROPAGATE_BLOCK, event.node_id, block))
        elif event.event_type == EventTypes.PROPAGATE_TXN:
            all_nodes[event.data["dest"]].capture_txn(event.data["trxn"])
        elif event.event_type == EventTypes.PROPAGATE_BLOCK:
            all_nodes[event.data["dest"]].capture_block(event.data["block"])

    def initialize_event_queue(self):
        for i in range(total_txn_blks):
            node = all_nodes[np.random.randint(0, len(all_nodes))]
            rand_event = random_val()
            if rand_event < txn_blk_ratio:
                node.generate_txn(np.random.choice(range(len(all_nodes))))
            else:
                node.mine_block()

    def _post_run(self, signum, frame):
        print("\nSimulation ended.")
        # for node in all_nodes.values():
            # print(f"Node {node.id}: Longest chain length = {node.blockchain.longest_chain_length}, Head = {node.blockchain.longest_chain_head}")
        sys.exit(0)

simulator = Simulator()