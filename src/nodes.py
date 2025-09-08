from enum import Enum
from transactions import Transaction
import numpy as np
from blockchain import Block 
txn_id  = 0
initial_coins = 100 ## change as needed

block_id = 1 # genesis block is 0
def get_block_id():
    global block_id
    block_id += 1
    return block_id

class NetworkSpeed(Enum):
    FAST = "fast"
    SLOW = "slow"
    
class CPUType(Enum):
    HIGH = "high"
    LOW = "low"
    
class Node:
    def __init__(self, id, cpu_type, network_speed):
        self.id = id
        self.neighbors = []
        self.coins = initial_coins
        self.genesis_block = Block(0, -1, self.id, 0) # confirm what to write @sarthak @svanik
        self.blockchain = [self.genesis_block] 
        self.longest_chain = [self.genesis_block]
        self.longest_chain_head = self.genesis_block.id
        self.longest_chain_length = 1
        self.cpu_type = cpu_type
        self.network_speed = network_speed
        self.hash_power = 1 if cpu_type == CPUType.LOW else 10
        self.mempool = []
        
        # add network delay function according to the formula
        # all_nodes[neighbor_id].network_delay
    def add_neighbor(self, neighbor_id):
        self.neighbors.append(neighbor_id)
        
    def generate_txn(self, dest_id):  
        amount = np.random.randint(1, self.coins)
        txn = Transaction(txn_id, self.id, dest_id, amount)
        self.mempool.append(txn)
        global txn_id
        txn_id += 1
        return txn
    
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

    def txns_in_longest_chain(self):
        txns = set()
        for block in self.longest_chain:
            for txn in block.transactions:
                txns.add(txn)
        return txns
    
    # to be completed
    def is_block_valid(self, block):
        # for txn in block.transactions:
        #     if txn not in self.mempool:
        #         return False
        #     sender = txn.sender
        #     receiver = txn.receiver
        #     amount = txn.amount
            
            # if all_nodes[sender].coins < amount:
            #     return False
            # elif all_nodes
        return True
    
    # @sarthak @svanik check where to update mempool, balances, reward etc
    # also check if coinbase txn should be added here or in block class
    def generate_block(self):
        
        txns = [txn for txn in self.mempool if txn not in self.txns_in_longest_chain()]
        selected_txns = []
        current_size = 8192 # coinbase txn size in bits
        for txn in txns:
            if current_size + txn.size <= 8192000:
                selected_txns.append(txn)
                current_size += txn.size

        blk_id = get_block_id()
        p_id = self.longest_chain_head
        candidate_block = Block(blk_id, p_id, self.id, 0)
        candidate_block.transactions.extend(selected_txns)
        I = 600
        Tk = np.random.exponential(I / self.hash_power)
        return candidate_block, Tk
