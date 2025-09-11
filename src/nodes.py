from modules import *
from blockchain import *
from events import *

class Node:
    def __init__(self, id, cpu_type, network_speed):
        self.id = id
        all_nodes[id] = self
        self.neighbors = []
        self.coins = initial_coins # reward for mining genesis block
        self.blockchain = None
        self.cpu_type = cpu_type
        self.network_speed = network_speed
        self.hash_power = 1 if cpu_type == CPUType.LOW else 10

    def blockchain_init(self): # This is needed to be added separately because first all nodes need to be init for all_nodes setup then blockchain for each is setup using that
        self.blockchain = Blockchain()

    def add_neighbor(self, neighbor_id):
        self.neighbors.append(neighbor_id)
    
    def generate_txn(self, dest_id):
        heapq.heappush(simulator.event_queue, Event(simulator.current_time + exp_random_val(T_tx), EventTypes.GENERATE_TXN, self.id, dest_id))

    # Mine a new block
    def mine_block(self):
        heapq.heappush(simulator.event_queue, Event(simulator.current_time + exp_random_val(T_interarrival/self.hash_power), EventTypes.GENERATE_BLOCK, self.id))
        # Update coin balance of node according to the longest chain head
        self.coins = self.blockchain.blocks[self.blockchain.longest_chain_head]["node_balances"].get(self.id, 0)

    # Capture a transaction
    def capture_txn(self, txn): 
        if self.blockchain.capture_txn(txn):
            # create events to propagate txn to neighbors
            for neighbor_id in self.neighbors:
                delay = self.network_delay(all_nodes[neighbor_id], tx_size)
                heapq.heappush(simulator.event_queue, Event(simulator.current_time + delay, EventTypes.PROPAGATE_TXN, neighbor_id, {"dest": neighbor_id, "trxn": txn}))

    # Capture a block 
    def capture_block(self, block):
        capture = self.blockchain.capture_block(block)
        # update coin balance of node according to the longest chain head
        self.coins = self.blockchain.blocks[self.blockchain.longest_chain_head]["node_balances"].get(self.id, 0)
        if capture != 0:
            # create events to propagate block to neighbors
            for neighbor_id in self.neighbors:
                delay = self.network_delay(all_nodes[neighbor_id], block.size)
                heapq.heappush(simulator.event_queue, Event(simulator.current_time + delay, EventTypes.PROPAGATE_BLOCK, neighbor_id, {"dest": neighbor_id, "block": block}))

    # Calculate network delay to another node based on speed and message size
    def network_delay(self, other_node, message_size):
        rho = np.random.uniform(rho_min, rho_max)   # seconds

        if self.network_speed == NetworkSpeed.FAST and other_node.network_speed == NetworkSpeed.FAST:
            c = c_fast
        else:
            c = c_slow

        transmission_delay = message_size / c
        mean_q_delay = 96 * 1024 / c
        d = exp_random_val(mean_q_delay)
        delay = rho + transmission_delay + d
        
        return delay

