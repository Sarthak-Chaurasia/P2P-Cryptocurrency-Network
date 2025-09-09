from modules import *
from transactions import *

class Block:
    def __init__(self, p_id, miner_id):
        self.p_id = p_id      # this is universally same for each block
        self.miner_id = miner_id
        self.transactions = [Transaction("coinbase", miner_id, reward)] # Every new transaction must have a coinbase transaction (SHOULD WE HAVE -1 in place of COINBASE @mugdha @svanik)
        self.creation_time = time.time()
        self.id = self.compute_hash()

    def compute_hash(self):
        blk = {
            "parent": str(self.p_id),
            "miner": str(self.miner_id),
            "transactions": [txn.trxn_id for txn in self.transactions]
        }
        data = json.dumps(blk, sort_keys=True)
        return sha256(data)
    
    def __str__(self):
        return f"Block {self.id[:3]} mined by Node {self.miner_id} containing {len(self.transactions)} transactions"
    
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

    def __str__(self):
        def dfs(block_id, prefix="", is_last=True):
            out = prefix + ("└─ " if is_last else "├─ ") + f"{block_id[:3]}\n"
            children = self.blocks[block_id]["children"]
            for i, child in enumerate(children):
                last = (i == len(children) - 1)
                new_prefix = prefix + ("   " if is_last else "│  ")
                out += dfs(child, new_prefix, last)
            return out

        return dfs(self.genesis.id, "", True)
    
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
        val = int(np.random.exponential(scale=sender.coins/10)) + 1
        amount = min(val, sender.coins)  # (@mugdha @svanik) should we make it more a distribution which picks more smaller values (exp distribution)
        txn = Transaction(sender.id, dest_id, amount)
        self.mempool.add(txn)
        return txn

    def capture_txn(self, txn): # add txn to mempool if not duplicate
        if txn not in self.mempool:
            self.mempool.add(txn)
            return True
        return False

    def mine_block(self, miner): # takes txns from mempool (assuming mempool is synced with longest chain) and generates a block (with transactions) and return Tk (time to mine??)
        self.sync_longest_chain()  # ensure longest chain is up to date before mining
        # txns = [txn for txn in self.mempool if txn not in self.txns_in_longest_chain()] # check in longest chain not necessary as we should update mempool everywhere to sync it with longest_chain
        txns = [txn for txn in self.mempool]
        selected_txns = []
        current_size = 8192 # coinbase txn size in bits
        for txn in txns:
            if current_size + txn.size <= 8192000: # @mugdha @svanik isn't 1000 transactions too big should we reduce it
                if self.blocks[self.longest_chain_head]["node_balances"][txn.sender] < txn.amount:
                    continue
                selected_txns.append(txn)
                current_size += txn.size

        p_id = self.longest_chain_head
        candidate_block = Block(p_id, miner.id)
        candidate_block.transactions.extend(selected_txns)
        I = 600
        Tk = np.random.exponential(I / miner.hash_power)
        return candidate_block, Tk

    def capture_block(self, block): # this should update the longest chain(if fork on tip) and mempool too (also update orphan pool and blocks(adj list))
        # no need to sync here
        if not self.is_block_valid(block):
            return False
        if block.id in self.blocks:
            return False  # Duplicate block, do nothing
        else:
            self.add_block(block) # ALL BLOCKS ARE ADDED IN blocks DICTIONARY, ORPHANS OR NOT

        if block.p_id in self.blocks:
            self.blocks[block.p_id]["children"].append(block.id)
            self.orphan_block_pool.discard(block.id)
        
            def update_orphan(block_id):
                orphans_parents = {self.blocks[blk_id]["block"].p_id : blk_id for blk_id in self.orphan_block_pool}
                if block_id in orphans_parents:
                    if self.add_orphan_to_blockchain(self.blocks[orphans_parents[block_id]]["block"]):
                        return True, orphans_parents[block_id]
                return False, None

            added = True
            block_id = block.id
            while added:
                added, block_id = update_orphan(block_id)

            if block.p_id == self.longest_chain_head:
                self.longest_chain.append(block.id)
                self.longest_chain_head = block.id
                self.longest_chain_length += 1
                for txn in block.transactions:
                    self.mempool.discard(txn)
        else:
            self.orphan_block_pool.add(block.id)
        return True

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

    def add_orphan_to_blockchain(self, orphan_block):
        if orphan_block.p_id in self.blocks:
            self.add_block(orphan_block)
            self.blocks[orphan_block.p_id]["children"].append(orphan_block.id)
            self.orphan_block_pool.discard(orphan_block.id)
            return True
