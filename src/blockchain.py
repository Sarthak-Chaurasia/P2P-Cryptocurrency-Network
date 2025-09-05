from nodes import *

class Block:
    def __init__(self, id, p_id, miner, creation_time):
        self.id = id
        self.p_id = p_id        # this is universally same for each block
        self.transactions = [coinbase_transaction] # Every new transaction must have a coinbase transaction
        self.miner = miner
        self.creation_time = creation_time

class Blockchain: # A unique copy of main blockchain held by each node (peer)
    def __init__(self,genesis):
        self.genesis = genesis
        self.blocks = {             # dictionary of blocks with children, node balances
            genesis.id: {
                "block": genesis,
                "children": [],
                "node_balances": {node: 0 for node in all_nodes_ids}
            }
        }
        self.orphan_block_pool = [] # list of block ids whose parent are yet to arrive
        self.mempool = [] # list of transactions waiting to be included in a block
        self.longest_chain_head = genesis.id
        self.longest_chain_length = 1


    def add_block(self, block):
        self.blocks[block.id] = {
            "block": block,
            "children": [],
            "node_balances": {node: 0 for node in all_nodes_ids}
        }