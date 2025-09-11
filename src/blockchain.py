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
        self.orphan_block_pool = {} # list of block ids whose parent are yet to arrive
        self.mempool = set() # list of transactions waiting to be included in a block
        self.longest_chain = [self.genesis.id]
        self.longest_chain_head = self.longest_chain[-1]
        self.longest_chain_transactions = set() # set of transactions in longest chain for quick lookup
        self.longest_chain_length = 1

    # String representation of the blockchain tree and longest chain
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
    
    # add a valid block to the blockchain (not orphan) and update longest chain and mempool accordingly
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
                "node_balances": temp_balances,
                "arrival_time": time.time()
            }

            self.blocks[block.p_id]["children"].append(block.id)
            self.orphan_block_pool.pop(block.id,None)

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
        self.longest_chain_head = self.longest_chain[-1]
        self.longest_chain_length = len(self.longest_chain)

    # generate a transaction from sender to dest_id with random amount and add to mempool
    def generate_txn(self, sender, dest_id):  
        val = int(np.random.exponential(sender.coins/20)) + 1
        amount = min(val, sender.coins/20)
        txn = Transaction(sender.id, dest_id, amount)
        self.mempool.add(txn)
        return txn

    # add txn to mempool if not duplicate or already in longest chain
    def capture_txn(self, txn):
        if txn not in self.mempool and txn not in self.longest_chain_transactions:
            self.mempool.add(txn)
            return True
        return False

    # takes txns from mempool (synced with longest chain) and generates a block (with coinbase and transactions subset) and return block
    def mine_block(self, miner):
        self.sync_longest_chain()  # ensure longest chain is up to date before mining
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

        if self.is_block_valid(mined_block) == 1:
            self.add_block(mined_block)

        return mined_block

    # capture a block (check if valid or orphan) and add to blockchain if valid, return -1 if orphan, 0 if invalid, 1 if added
    def capture_block(self, block):
        # no need to sync here
        if block.id in self.blocks or block.id in self.orphan_block_pool:
            return 0 # duplicate block, do nothing
        
        validity = self.is_block_valid(block)
        if validity == -1:
            self.orphan_block_pool[block.id] = block
            return -1 # captured but as orphan
        elif validity == 0:
            return 0 # invalid block, DROP
        #else valid block, proceed

        self.add_block(block)
    
        # Function to add orphan blocks whose parents have just been added
        def update_orphan(block_id):
            orphan_parents = {}
            for blk in self.orphan_block_pool.values():
                orphan_parents.setdefault(blk.p_id, []).append(blk)
            if block_id in orphan_parents:
                added_orphan_blocks = []
                for orphan_block in orphan_parents[block_id]:
                    if self.is_block_valid(orphan_block) == 1:
                        self.add_block(orphan_block)
                        added_orphan_blocks.append(orphan_block.id)
                return added_orphan_blocks
            return []


        # Check if any orphans can now be added
        added_blocks = deque([block.id])

        while added_blocks:
            blk_id = added_blocks.popleft()
            new_orphans = update_orphan(blk_id)
            added_blocks.extend(new_orphans)

        return 1

    # returns False if invalid or orphan
    def is_block_valid(self,block):
        if block.p_id not in self.blocks.keys():
            return -1 # orphan block
        
        temp_balances = self.blocks[block.p_id]["node_balances"].copy()
        for txn in block.transactions:
            sender = txn.sender
            receiver = txn.receiver
            amount = txn.amount

            if sender != "coinbase":
                if temp_balances[sender] < amount:
                    return 0
                else:
                    temp_balances[sender] -= amount
                    temp_balances[receiver] += amount
            else:
                temp_balances[receiver] += amount
        return 1

    # to create json of block arrival times
    def to_json_nodeblocks_arrival(self):
        data = {}
        for bid, info in self.blocks.items():
            data[bid] = info["arrival_time"]
        return data
    
    # returns [r1_high_cpu, r1_low_cpu, r1_fast, r1_slow, r2_high_cpu, r2_low_cpu, r2_fast, r2_slow]
    def get_ratio_of_blocks(self):
        # Blocks in longest chain per node
        block_count_in_longest_chain = {node: 0 for node in all_nodes}
        for blk_id in self.longest_chain:
            block = self.blocks[blk_id]["block"]
            if block.miner_id != -1:
                block_count_in_longest_chain[block.miner_id] += 1

        # Total blocks in the whole tree per node
        total_block_count = {node: 0 for node in all_nodes}

        def dfs(block_id):
            block = self.blocks[block_id]["block"]
            if block.miner_id != -1:
                total_block_count[block.miner_id] += 1
            for child_id in self.blocks[block_id]["children"]:
                dfs(child_id)

        dfs(self.genesis.id)

        # Ratio (longest_chain / total mined) per node
        ratio = {}
        for node in all_nodes:
            if total_block_count[node] > 0:
                ratio[node] = block_count_in_longest_chain[node] / total_block_count[node]
            else:
                ratio[node] = 0.0

        slow_ratios, fast_ratios = [], []
        high_cpu_ratios, low_cpu_ratios = [], []

        # Contribution accumulators
        slow_contrib, fast_contrib = 0, 0
        high_cpu_contrib, low_cpu_contrib = 0, 0
        longest_chain_len = len(self.longest_chain)

        for node, r in ratio.items():
            # Group by network speed
            if all_nodes[node].network_speed == NetworkSpeed.FAST:
                fast_ratios.append(r)
                fast_contrib += block_count_in_longest_chain[node]
            else:
                slow_ratios.append(r)
                slow_contrib += block_count_in_longest_chain[node]

            # Group by CPU type
            if all_nodes[node].cpu_type == CPUType.HIGH:
                high_cpu_ratios.append(r)
                high_cpu_contrib += block_count_in_longest_chain[node]
            elif all_nodes[node].cpu_type == CPUType.LOW:
                low_cpu_ratios.append(r)
                low_cpu_contrib += block_count_in_longest_chain[node]

        # Average ratios per group
        r1_slow = sum(slow_ratios) / len(slow_ratios) if slow_ratios else 0.0
        r1_fast = sum(fast_ratios) / len(fast_ratios) if fast_ratios else 0.0
        r1_high_cpu = sum(high_cpu_ratios) / len(high_cpu_ratios) if high_cpu_ratios else 0.0
        r1_low_cpu = sum(low_cpu_ratios) / len(low_cpu_ratios) if low_cpu_ratios else 0.0

        # Contribution per group 
        r2_slow = slow_contrib / longest_chain_len if longest_chain_len > 0 else 0.0
        r2_fast = fast_contrib / longest_chain_len if longest_chain_len > 0 else 0.0
        r2_high_cpu = high_cpu_contrib / longest_chain_len if longest_chain_len > 0 else 0.0
        r2_low_cpu = low_cpu_contrib / longest_chain_len if longest_chain_len > 0 else 0.0

        results = [r1_high_cpu, r1_low_cpu, r1_fast, r1_slow, r2_high_cpu, r2_low_cpu, r2_fast, r2_slow]
        return results
    
    # Visualize the blockchain tree using networkx and matplotlib
    def draw_blockchain_tree(self):
        G = nx.DiGraph()
        # Add edges (parent -> child)
        for blk_id, data in self.blocks.items():
            for child in data["children"]:
                G.add_edge(blk_id, child)

        # Position nodes using hierarchy
        pos = nx.nx_agraph.graphviz_layout(G, prog="dot")

        # Draw all nodes
        nx.draw(G, pos, with_labels=False, node_size=30, node_color="lightblue", arrows=True)

        # Highlight the longest chain
        longest_edges = [(self.longest_chain[i], self.longest_chain[i+1]) 
                        for i in range(len(self.longest_chain)-1)]
        nx.draw_networkx_edges(G, pos, edgelist=longest_edges, edge_color="red", width=2)
        nx.draw_networkx_nodes(G, pos, nodelist=self.longest_chain, node_color="orange", node_size=50)

        # Label nodes with block short-ids
        labels = {blk_id: blk_id[:3] for blk_id in G.nodes}
        nx.draw_networkx_labels(G, pos, labels, font_size=8)

        plt.title("Blockchain Tree (Longest Chain Highlighted)")
        plt.savefig("images/blockchain_tree.png")