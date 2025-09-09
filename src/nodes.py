from modules import *
from blockchain import *
from events import *

initial_coins = 100 ## change as needed

class NetworkSpeed(Enum):
    FAST = "fast"
    SLOW = "slow"
    
class CPUType(Enum):
    HIGH = "high"
    LOW = "low"
    
class Node:
    def __init__(self, id, cpu_type, network_speed):
        self.id = id
        all_nodes[id] = self
        self.neighbors = []
        self.coins = initial_coins
        self.blockchain = None
        self.cpu_type = cpu_type
        self.network_speed = network_speed
        self.hash_power = 1 if cpu_type == CPUType.LOW else 10
        # self.mempool = []

    def blockchain_init(self): # This is needed to be added separately because first all nodes need to be init for all_nodes setup then blockchain for each is setup using that
        self.blockchain = Blockchain()

        # add network delay function according to the formula
        # all_nodes[neighbor_id].network_delay
    def add_neighbor(self, neighbor_id):
        self.neighbors.append(neighbor_id)
    
    def generate_txn(self, dest_id):
        heapq.heappush(simulator.event_queue, Event(0, EventTypes.GENERATE_TXN, self.id, dest_id))
        # simulator.event_queue.append(Event(0, EventTypes.GENERATE_TXN, self.id, dest_id))
    
    def mine_block(self):
        heapq.heappush(simulator.event_queue, Event(0, EventTypes.GENERATE_BLOCK, self.id))

    def capture_txn(self, txn): 
        self.blockchain.capture_txn(txn)

    def capture_block(self, block):
        self.blockchain.capture_block(block)

    def network_delay(self, other_node, message_size):
        rho = np.random.uniform(10, 500) / 1000.0   # seconds
        if self.network_speed == NetworkSpeed.FAST and other_node.network_speed == NetworkSpeed.FAST:
            c = 100000000
        else:
            c = 5000000     # 5 Mbps = 5 * 10^6 bits/sec

        transmission_delay = message_size / c
        mean_q_delay = 96000 / c
        d = np.random.exponential(mean_q_delay)
        delay = rho + transmission_delay + d
        
        return delay

    # (IN blockchain.py)
    # def txns_in_longest_chain(self):
    #     txns = set()
    #     for block in self.blockchain.longest_chain:
    #         for txn in block.transactions:
    #             txns.add(txn)
    #     return txns
    
    # def is_block_valid(self, block): # DONE in blockchain.py
    
    # (IN blockchain.py) @sarthak @svanik check where to update mempool, balances, reward etc
    # also check if coinbase txn should be added here or in block class
    # def generate_block(self):
        
    #     txns = [txn for txn in self.mempool if txn not in self.txns_in_longest_chain()]
    #     selected_txns = []
    #     current_size = 8192 # coinbase txn size in bits
    #     for txn in txns:
    #         if current_size + txn.size <= 8192000:
    #             selected_txns.append(txn)
    #             current_size += txn.size

    #     p_id = self.blockchain.longest_chain_head
    #     candidate_block = Block(p_id, self.id)
    #     candidate_block.transactions.extend(selected_txns)
    #     I = 600
    #     Tk = np.random.exponential(I / self.hash_power)
    #     return candidate_block, Tk
