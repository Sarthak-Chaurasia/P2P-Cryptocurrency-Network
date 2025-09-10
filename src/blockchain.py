from matplotlib.pylab import block
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

    def __lt__(self, other):
        return self.id < other.id
    
    @property
    def size(self):
        return len(self.transactions) * tx_size

genesis_block = Block(-1, -1)

class Blockchain: # A unique copy of main blockchain held by each node (peer)
    def __init__(self):
        self.genesis = genesis_block
        self.blocks = {             # dictionary of blocks with children, node balances (ACTING LIKE AND ADJACENCY LIST)
            self.genesis.id: {
                "block": self.genesis,
                "children": [],
                "node_balances": {node: int(all_nodes[node].coins) for node in all_nodes},
                "arrival_time": time.time()
            }
        }
        self.orphan_block_pool = set() # list of block ids whose parent are yet to arrive
        self.mempool = set() # list of transactions waiting to be included in a block
        self.longest_chain = [self.genesis.id]
        self.longest_chain_head = self.longest_chain[-1]
        self.longest_chain_transactions = set() # set of transactions in longest chain for quick lookup
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

        return dfs(self.genesis.id, "", True) + "\n" +  " -> ".join([bid[:3] for bid in self.longest_chain])
        # return " -> ".join([bid[:3] for bid in self.longest_chain])
    
    def add_block(self, block): # only add valid non-orphan blocks
        if block.p_id in self.blocks:
            temp_balances = self.blocks[block.p_id]["node_balances"].copy()
            for txn in block.transactions:
                sender = txn.sender
                receiver = txn.receiver
                amount = txn.amount

                if sender != "coinbase":
                    temp_balances[sender] -= amount
                    temp_balances[receiver] += amount
                else:
                    temp_balances[receiver] += amount

            self.blocks[block.id] = {
                "block": block,
                "children": [],
                "node_balances": {node: temp_balances.get(node, 0) for node in all_nodes},
                "arrival_time": time.time()
            }

            self.blocks[block.p_id]["children"].append(block.id)
            self.orphan_block_pool.discard(block)

            if block.p_id == self.longest_chain_head:
                self.longest_chain.append(block.id)
                self.longest_chain_head = block.id
                self.longest_chain_length += 1
                for txn in block.transactions:
                    self.mempool.discard(txn)
                    self.longest_chain_transactions.add(txn)
    
    def sync_longest_chain(self): # run this time to time to update longest chain and mempool also (RUN BEFORE MINING)
        # find the longest chain by DFS or BFS
        def longest_path_from(self, block_id):
            def dfs(bid):
                children = self.blocks[bid]["children"]
                if not children:
                    return [bid]   # leaf -> path is just itself
                # pick child with longest path
                longest = []
                for child in children:
                    path = dfs(child)
                    if len(path) > len(longest):
                        longest = path
                return [bid] + longest

            return dfs(block_id)
        longest_path = longest_path_from(self, self.genesis.id)

        # print("Before")
        #print longchain and long path
        # print("Longest Chain: ", " -> ".join([bid[:3] for bid in self.longest_chain]))
        # print("Longest Path:  ", " -> ".join([bid[:3] for bid in longest_path]))
        
        # self.longest_chain = [self.blocks[bid]["block"] for bid in longest_path] # this is in efficient, can be optimized
        def pivot():
            longest_path_set = set(longest_path)
            for blk_id in reversed(self.longest_chain):
                if blk_id in longest_path_set:
                    # print(f"Pivot at block {blk_id[:3]}, next longchain {longest_path[longest_path.index(blk_id)+1][:3]}, next longpath {longest_path[longest_path.index(blk_id)+1][:3]}")
                    # print(f"Pivot at block {blk_id[:3]}")
                    # add transactions back to mempool
                    for b_id in self.longest_chain[self.longest_chain.index(blk_id)+1:]:
                        for txn in self.blocks[b_id]["block"].transactions:
                            if txn.sender != "coinbase":
                                self.mempool.add(txn)
                                self.longest_chain_transactions.discard(txn)
                    # remove blocks after pivot from longest chain and add new blocks to longest chain
                    self.longest_chain = self.longest_chain[:self.longest_chain.index(blk_id)+1]
                    self.longest_chain.extend(longest_path[longest_path.index(blk_id)+1:])
                    # remove transactions from mempool for added blocks
                    pivot_index = longest_path.index(blk_id)
                    for b_id in longest_path[pivot_index + 1:]:
                        for txn in self.blocks[b_id]["block"].transactions:
                            self.mempool.discard(txn)
                            self.longest_chain_transactions.add(txn)
                    return
        
        pivot()
        # print("After")
        # print("Longest Chain: ", " -> ".join([bid[:3] for bid in self.longest_chain]))
        # print("Longest Path:  ", " -> ".join([bid[:3] for bid in longest_path]))
        self.longest_chain_head = self.longest_chain[-1]
        self.longest_chain_length = len(self.longest_chain)

    def generate_txn(self, sender, dest_id):  
        val = int(np.random.exponential(scale=sender.coins/10)) + 1
        amount = min(val, sender.coins)
        txn = Transaction(sender.id, dest_id, amount)
        self.mempool.add(txn)
        return txn

    def capture_txn(self, txn): # add txn to mempool if not duplicate
        if txn not in self.mempool and txn not in self.longest_chain_transactions:
            self.mempool.add(txn)
            return True
        return False

    def mine_block(self, miner): # takes txns from mempool (assuming mempool is synced with longest chain) and generates a block (with transactions) and return Tk (time to mine??)
        # print("Node: ", miner.id, "is mining a block with head: ", self.longest_chain_head[:3]," and root : ", self.longest_chain[0][:3])
        self.sync_longest_chain()  # ensure longest chain is up to date before mining
        # print("After sync, longest chain head: ", self.longest_chain_head[:3]," and root : ", self.longest_chain[0][:3])
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
        mined_block = Block(p_id, miner.id)
        mined_block.transactions.extend(selected_txns)

        if self.is_block_valid(mined_block):
            self.add_block(mined_block)
            
        # I = 600
        # Tk = np.random.exponential(I / miner.hash_power)
        # return mined_block, Tk
        return mined_block

    def capture_block(self, block): # this should update the longest chain(if fork on tip) and mempool too (also update orphan pool and blocks(adj list))
        # no need to sync here
        if block.id in self.blocks or block in self.orphan_block_pool:
            return False # duplicate block, do nothing
        
        validity = self.is_block_valid(block)
        if validity == 0:
            self.orphan_block_pool.add(block)
            return 1 # captured but as orphan
        elif validity == False:
            return False # invalid block, DROP
        #else valid block, proceed

        self.add_block(block)
    
        def update_orphan(block_id):
            orphan_parents = {}
            for blk in self.orphan_block_pool:
                orphan_parents.setdefault(blk.p_id, []).append(blk)
            if block_id in orphan_parents:
                added_orphan_blocks = []
                for orphan_block in orphan_parents[block_id]:
                    if self.is_block_valid(orphan_block):
                        self.add_block(orphan_block)
                        added_orphan_blocks.append(orphan_block.id)
                return added_orphan_blocks
            return []


        added_blocks = deque([block.id])

        while added_blocks:
            blk_id = added_blocks.popleft()
            new_orphans = update_orphan(blk_id)
            added_blocks.extend(new_orphans)

        # added = True
        # added_blocks = [block.id]
        # while added:
        #     new_added = []
        #     for blk_id in added_blocks:
        #         added, yoyo = update_orphan(blk_id)
        #         if added:
        #             new_added.extend(yoyo)
        #     added_blocks = new_added

        return True

    def is_block_valid(self,block): # returns False if invalid or orphan
        if block.p_id not in self.blocks:
            return 0 # orphan block
        
        temp_balances = self.blocks[block.p_id]["node_balances"].copy()
        for txn in block.transactions:
            sender = txn.sender
            receiver = txn.receiver
            amount = txn.amount

            if sender != "coinbase":
                if temp_balances[sender] < amount:
                    return False
                else:
                    temp_balances[sender] -= amount
                    temp_balances[receiver] += amount
            else:
                temp_balances[receiver] += amount
        return True

    def add_orphan_to_blockchain(self, orphan_block): #nothing special can do directly
        if self.is_block_valid(orphan_block):
            self.add_block(orphan_block)
            return True
        return False
