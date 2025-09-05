all_nodes_ids = []

class Node:
    def __init__(self, id, cpu_type, network_speed, blockchain):
        self.id = id
        self.neighbours = []
        self.cpu_type = cpu_type
        self.network_speed = network_speed
        self.blockchain = blockchain
        all_nodes_ids.append(id)