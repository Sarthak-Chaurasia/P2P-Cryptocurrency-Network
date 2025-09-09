from modules import *

class Transaction:
    def __init__(self, sender, receiver, amount):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.time = time.time()
        self.size = 8192 # 1KB in bits 
        self.trxn_id = self.compute_hash(sender, receiver, amount, time)

    def compute_hash(self, sender, receiver, amount, time):
        txn = {
            "sender": sender,
            "receiver": receiver,
            "amount": amount,
            "time": time
        }
        data = json.dumps(txn, sort_keys=True)
        return sha256(data)

    def __str__(self):
        return f"{self.trxn_id}: {self.sender} pays {self.receiver} {self.amount} coins"