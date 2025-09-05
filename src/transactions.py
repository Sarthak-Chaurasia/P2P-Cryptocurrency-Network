class Transaction:
    def __init__(self, trxn_id, sender, receiver, amount):
        self.trxn_id = trxn_id
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.size = 8192 # 1KB in bits 

    def __str__(self):
        return f"{self.trxn_id}: {self.sender} pays {self.receiver} {self.amount} coins"