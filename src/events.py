from modules import *

# All events that are scheduled need to be defined here
class EventTypes(Enum):
    GENERATE_TXN = "generate a new transaction on node and add propagate to event queue"
    GENERATE_BLOCK = "generate a new block on node and add propagate to event queue"
    PROPAGATE_TXN = "propagate txn to neighbors of node"
    PROPAGATE_BLOCK = "propagate block to neighbors of node"
    # TRANSMIT_TXN = "send transmit_txn to event handler to generate capture_txn for neighbors"
    # CAPTURE_TXN = "send capture_txn to nodes to generate transmit_txn for broadcasting"
    # TRANSMIT_BLOCK = "send transmit_block to event handler to generate capture_block for neighbors"
    # CAPTURE_BLOCK = "send capture_block to nodes to generate transmit_block for broadcasting"

# Event class; event queue will be a global priority queue, not node specific
class Event:
    def __init__(self, time, event_type, node_id, data=None):
        self.time = time
        self.event_type = event_type
        self.node_id = node_id  # the node on which the event occurs
        self.data = data
    
    def __lt__(self, other):
        return self.time < other.time
    
    def __str__(self):
        return f"Time {self.time:.5f}: Node {self.node_id} {self.event_type.value}"
    
class Simulator:
    def __init__(self):
        self.event_queue = []
    
    def handle_event(self, event):
        if event.event_type == EventTypes.GENERATE_TXN:
            txn = all_nodes[event.node_id].blockchain.generate_txn(all_nodes[event.node_id], event.data)
            # self.event_queue.append(Event(event.time, EventTypes.PROPAGATE_TXN, all_nodes[event.node_id].id, txn))
            heapq.heappush(self.event_queue, Event(event.time, EventTypes.PROPAGATE_TXN, event.node_id, txn))
        elif event.event_type == EventTypes.GENERATE_BLOCK:
            block, tk = all_nodes[event.node_id].blockchain.mine_block(all_nodes[event.node_id])
            # self.event_queue.append(Event(event.time, EventTypes.PROPAGATE_BLOCK, all_nodes[event.node_id].id, block))
            heapq.heappush(self.event_queue, Event(event.time + tk, EventTypes.PROPAGATE_BLOCK, event.node_id, block))
        elif event.event_type == EventTypes.PROPAGATE_TXN:
            for neighbor_id in all_nodes[event.node_id].neighbors:
                # delay = all_nodes[event.node_id].network_delay(all_nodes[neighbor_id], event.data.size)
                all_nodes[neighbor_id].capture_txn(event.data)
        elif event.event_type == EventTypes.PROPAGATE_BLOCK:
            for neighbor_id in all_nodes[event.node_id].neighbors:
                # delay = all_nodes[event.node_id].network_delay(all_nodes[neighbor_id], event.data.size)
                all_nodes[neighbor_id].capture_block(event.data)

    # def send_txn(self, event):
    #     print(f"Sending transaction event: {event}")
    #     all_nodes[event.node_id].mempool.append(event.data)
    #     for neighbor_id in all_nodes[event.node_id].neighbors:
    #         heapq.heappush(event_list, Event(event.time + all_nodes[event.node_id].network_delay(all_nodes[neighbor_id], event.data.size), EventTypes.RECEIVE_TXN, neighbor_id, event.data))

    # def receive_txn(self, event):
    #     if event.data in all_nodes[event.node_id].mempool:
    #         print("Duplicate transaction received, discarding")
    #         return  # Discard duplicate transaction
    #     print(f"Node {event.node_id} received transaction {event.data.id}")
    #     all_nodes[event.node_id].mempool.append(event.data)
    #     for neighbor_id in all_nodes[event.node_id].neighbors:
    #         heapq.heappush(event_list, Event(event.time + all_nodes[event.node_id].network_delay(all_nodes[neighbor_id], event.data.size), EventTypes.RECEIVE_TXN, neighbor_id, event.data))
            
    # def send_block(self, event):
    #     all_nodes[event.node_id].blockchain.append(event.data)
    #     print(f"Sending block event: {event}")
    #     for neighbor_id in all_nodes[event.node_id].neighbors:
    #         heapq.heappush(event_list, Event(event.time + all_nodes[event.node_id].network_delay(all_nodes[neighbor_id], event.data.size), EventTypes.RECEIVE_BLOCK, neighbor_id, event.data))

    # def receive_block(self, event):
    #     if event.data in all_nodes[event.node_id].blockchain:
    #         print("Duplicate block received, discarding")
    #         return  
        
    #     # check if is valid function should be in block or in node
    #     if all_nodes[event.node_id].is_block_valid(event.data):
    #         all_nodes[event.node_id].blockchain.append(event.data)
    #         for txn in event.data.transactions:
    #             if txn in all_nodes[event.node_id].mempool:
    #                 all_nodes[event.node_id].mempool.remove(txn)
                    
    #     print(f"Node {event.node_id} received block {event.data.id}")
    #     for neighbor_id in all_nodes[event.node_id].neighbors:
    #         heapq.heappush(event_list, Event(event.time + all_nodes[event.node_id].network_delay(all_nodes[neighbor_id], event.data.size), EventTypes.RECEIVE_BLOCK, neighbor_id, event.data))

simulator = Simulator()
    