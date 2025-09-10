from modules import *
from nodes import *

def is_connected(nodes):
    if not nodes:
        return True
    start_id = next(iter(nodes))
    visited = set()
    q = deque([start_id])
    visited.add(start_id)
    while q:
        u = q.popleft()
        for v in nodes[u].neighbors:
            if v not in visited:
                visited.add(v)
                q.append(v)
    return len(visited) == len(nodes)

def make_connected_graph(n, seed, node_speeds, node_cpus):

    if seed is not None:
        random.seed(seed)

    while True:  
        nodes = {i: Node(i, node_cpus[i], node_speeds[i]) for i in range(n)}
        for node in nodes.values():
            node.blockchain_init()
        degrees = {i: 0 for i in range(n)}
        edges: Set[frozenset[int]] = set()

        ids = list(nodes.keys())
        random.shuffle(ids)
        for i in range(1, n):
            u = ids[i]
            v = random.choice(ids[:i])
            nodes[u].add_neighbor(v)
            nodes[v].add_neighbor(u)
            edges.add(frozenset([u, v]))
            degrees[u] += 1
            degrees[v] += 1

        attempts = 0
        while attempts < n * n:
            u, v = random.sample(range(n), 2)
            if degrees[u] >= 6 or degrees[v] >= 6:
                attempts += 1
                continue
            if frozenset([u, v]) in edges:
                attempts += 1
                continue
            
            nodes[u].add_neighbor(v)
            nodes[v].add_neighbor(u)
            edges.add(frozenset([u, v]))
            degrees[u] += 1
            degrees[v] += 1
            
            if all(3 <= degrees[i] <= 6 for i in range(n)):
                break
            attempts += 1

        if not all(3 <= degrees[i] <= 6 for i in range(n)):
            continue 
        
        if is_connected(nodes):
            return nodes

