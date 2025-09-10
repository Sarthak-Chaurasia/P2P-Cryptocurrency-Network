import numpy as np
import heapq
import hashlib
import json
import time
import signal
import sys
from enum import Enum
import random
from typing import Dict, Set
from collections import deque

class NetworkSpeed(Enum):
    FAST = "fast"
    SLOW = "slow"
    
class CPUType(Enum):
    HIGH = "high"
    LOW = "low"
    
all_nodes = {}

n: int  # number of nodes
z0: float # ratio of slow nodes
z1: float # ratio of low CPU power nodes
T_tx: float # inter arrival time between transactions
T_interarrival: float # inter arrival time between blocks
timeout = None # timeout for simulation, None for our purposes, we end simulation with SigInt
visualize: bool # enable visualization

## Constants
initial_coins = 100 ## change as needed

# Network speeds in Mbps
c_fast: int = 100
c_slow: int = 5
d_const: float = 96e-3

# Speed of light in s
rho_min: float = 10e-3
rho_max: float = 500e-3

# Transaction and block sizes in Mb
tx_size: float = 8e-3
block_max_size: int = 8

# Reward and initial balance in coins
init_balance: int = 0
reward: int = 50

# Number of neighbors
n_low: int = 3
n_high: int = 6

# Hash power multiplier
hash_power_mult: int = 10

def sha256(data):
    return hashlib.sha256(data.encode()).hexdigest()

def random_val():
    return np.random.uniform(0, 1)

def exp_random_val():
    return np.random.exponential(1)