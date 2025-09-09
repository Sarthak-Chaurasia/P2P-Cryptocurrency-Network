from modules import *
from transactions import *

class Block:
    def __init__(self, p_id, miner):
        self.p_id = p_id      # this is universally same for each block
        self.transactions = [Transaction("coinbase", miner, reward)] # Every new transaction must have a coinbase transaction (SHOULD WE HAVE -1 in place of COINBASE @mugdha @svanik)
        self.miner = miner
        self.creation_time = time.time()
        self.id = self.compute_hash()

    def compute_hash(self):
        blk = {
            "parent": self.p_id,
            "miner": self.miner,
            "transactions": [txn.trxn_id for txn in self.transactions]
        }
        data = json.dumps(blk, sort_keys=True)
        return sha256(data)

genesis_block = Block(-1, -1)

class Blockchain: # A unique copy of main blockchain held by each node (peer)
    def __init__(self):
        self.genesis = genesis_block
        self.blocks = {             # dictionary of blocks with children, node balances (ACTING LIKE AND ADJACENCY LIST)
            self.genesis.id: {
                "block": self.genesis,
                "children": [],
                "node_balances": {node: 0 for node in all_nodes}
            }
        }
        self.orphan_block_pool = set() # list of block ids whose parent are yet to arrive
        self.mempool = set() # list of transactions waiting to be included in a block
        self.longest_chain = [self.genesis.id]
        self.longest_chain_head = self.longest_chain[-1]
        self.longest_chain_length = 1


    def add_block(self, block):
        self.blocks[block.id] = {
            "block": block,
            "children": [],
            "node_balances": {node: 0 for node in all_nodes}
        }
    
    def sync_longest_chain(self): # run this time to time to update longest chain and mempool also (RUN BEFORE MINING)
        # find the longest chain by DFS or BFS
        def dfs(block_id, path):
            path.append(block_id)
            if not self.blocks[block_id]["children"]:
                return [path[:]]
            paths = []
            for child_id in self.blocks[block_id]["children"]:
                paths.extend(dfs(child_id, path))
            path.pop()
            return paths
        
        all_paths = dfs(self.genesis.id, [])
        longest_path = max(all_paths, key=len)
        
        # self.longest_chain = [self.blocks[bid]["block"] for bid in longest_path] # this is in efficient, can be optimized
        def pivot():
            longest_path_set = set(longest_path)
            for blk_id in reversed(self.longest_chain):
                if blk_id in longest_path_set:
                    # add transactions back to mempool
                    for b_id in self.longest_chain[self.longest_chain.index(blk_id)+1:]:
                        for txn in self.blocks[b_id]["block"].transactions:
                            if txn.sender != "coinbase":
                                self.mempool.add(txn)
                    # remove blocks after pivot from longest chain
                    self.longest_chain = self.longest_chain[self.longest_chain.index(blk_id):]
                    # add new blocks to longest chain
                    pivot_index = longest_path.index(blk_id)
                    for b_id in longest_path[pivot_index + 1:]:
                        self.longest_chain.append(self.blocks[b_id]["block"].id)
                    # remove transactions from mempool for added blocks
                    for b_id in longest_path[pivot_index + 1:]:
                        for txn in self.blocks[b_id]["block"].transactions:
                            self.mempool.discard(txn)
                    return
        
        pivot()
        self.longest_chain_head = self.longest_chain[-1]
        self.longest_chain_length = len(self.longest_chain)

    def generate_txn(self, sender, dest_id):  
        amount = np.random.randint(1, sender.coins) # (@mugdha @svanik) should we make it more a distribution which picks more smaller values (exp distribution)
        txn = Transaction(sender.id, dest_id, amount)
        self.mempool.add(txn)
        return txn

    def capture_txn(self, txn): # add txn to mempool if not duplicate
        self.mempool.add(txn)

    def mine_block(self, miner): # takes txns from mempool (assuming mempool is synced with longest chain) and generates a block (with transactions) and return Tk (time to mine??)
        self.sync_longest_chain()  # ensure longest chain is up to date before mining
        # txns = [txn for txn in self.mempool if txn not in self.txns_in_longest_chain()] # check in longest chain not necessary as we should update mempool everywhere to sync it with longest_chain
        txns = [txn for txn in self.mempool]
        selected_txns = []
        current_size = 8192 # coinbase txn size in bits
        for txn in txns:
            if current_size + txn.size <= 8192000: # @mugdha @svanik isn't 1000 transactions too big should we reduce it
                selected_txns.append(txn)
                current_size += txn.size

        p_id = self.longest_chain_head
        candidate_block = Block(p_id, miner)
        candidate_block.transactions.extend(selected_txns)
        I = 600
        Tk = np.random.exponential(I / miner.hash_power)
        return candidate_block, Tk

    def capture_block(self, block): # this should update the longest chain(if fork on tip) and mempool too (also update orphan pool and blocks(adj list))
        # no need to sync here
        if not self.is_block_valid(block):
            return
        if block.id in self.blocks:
            return  # Duplicate block, do nothing
        else:
            self.add_block(block)

        if block.p_id in self.blocks:
            self.blocks[block.p_id]["children"].append(block.id)
            self.orphan_block_pool.discard(block.id)
        else:
            self.orphan_block_pool.add(block.id)
            return

        if block.p_id == self.longest_chain_head:
            self.longest_chain.append(block.id)
            self.longest_chain_head = block.id
            self.longest_chain_length += 1
            for txn in block.transactions:
                self.mempool.discard(txn)

    def is_block_valid(self,block): # returns if block is valid also updates orphan block pool, blocks(adj list)
        # check if parent exists
        if block.p_id not in self.blocks:
            self.orphan_block_pool.add(block.id)
            return False
        
        # check if transactions are valid
        temp_balances = self.blocks[block.p_id]["node_balances"].copy()
        for txn in block.transactions:
            sender = txn.sender
            receiver = txn.receiver
            amount = txn.amount
            
            if sender != "coinbase":
                if temp_balances[sender] < amount:
                    return False # discarding the block not adding to orphan pool
                else:
                    temp_balances[sender] -= amount
                    temp_balances[receiver] += amount
            else:
                temp_balances[receiver] += amount
        
        self.add_block(block)
        self.blocks[block.p_id]["children"].append(block.id)
        self.blocks[block.id]["node_balances"] = temp_balances
        
        return True


