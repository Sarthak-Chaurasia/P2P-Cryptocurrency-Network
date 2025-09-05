
# the four types of events that can occur in the simulation
class EventTypes(enum.Enum):
    TRANSMIT_TXN = "send transmit_txn to event handler to generate capture_txn for neighbors"
    CAPTURE_TXN = "send capture_txn to nodes to generate transmit_txn for broadcasting"
    TRANSMIT_BLOCK = "send transmit_block to event handler to generate capture_block for neighbors"
    CAPTURE_BLOCK = "send capture_block to nodes to generate transmit_block for broadcasting"

# Event class; event queue will be a global priority queue, not node specific
class Event:
    def __init__(self, time, event_type, node_id, data=None):
        self.time = time
        self.event_type = event_type
        self.node_id = node_id  # the node on which the event occurs
        self.data = data
    
    def __str__(self):
        return f"Time {self.time:.5f}: Node {self.node_id} {self.event_type.value}"