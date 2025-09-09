from modules import *

class Transaction:
    def __init__(self, sender, receiver, amount):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.txn_time = time.time()
        self.size = 8192 # 1KB in bits
        self.trxn_id = self.compute_hash(self.sender, self.receiver, self.amount, self.txn_time)

    def compute_hash(self, sender, receiver, amount, txn_time):
        txn = {
            "sender": str(sender),
            "receiver": str(receiver),
            "amount": int(amount),
            "time": float(txn_time)
        }
        data = json.dumps(txn, sort_keys=True)
        return sha256(data)

    def __str__(self):
        # return f"{self.trxn_id}: {self.sender} pays {self.receiver} {self.amount} coins"
        return f"{self.sender} pays {self.receiver} {self.amount} coins"
