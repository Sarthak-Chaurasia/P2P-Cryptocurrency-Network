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
from matplotlib.pylab import block
import networkx as nx
import matplotlib.pyplot as plt

all_nodes = {}

n: int  # number of nodes
z0: float # ratio of slow nodes
z1: float # ratio of low CPU power nodes
T_tx: float # inter arrival time between transactions
T_interarrival: float # inter arrival time between blocks
timeout = None # timeout for simulation, None for our purposes, we end simulation with SigInt
visualize: bool # enable visualization

n = 10 if len(sys.argv) < 2 or sys.argv[1] == -1 else int(sys.argv[1])  # number of nodes
z0 = 0.3 if len(sys.argv) < 3 or sys.argv[2] == -1 else float(sys.argv[2])  # ratio of slow nodes
z1 = 0.3 if len(sys.argv) < 4 or sys.argv[3] == -1 else float(sys.argv[3])  # ratio of low CPU power nodes
T_tx = 1.0 if len(sys.argv) < 5 or sys.argv[4] == -1 else float(sys.argv[4])  # mean inter-arrival time between transactions
T_interarrival = 10.0 if len(sys.argv) < 6 or sys.argv[5] == -1 else float(sys.argv[5])  # mean inter-arrival time between blocks
txn_blk_ratio = 0.6 if len(sys.argv) < 7 or sys.argv[6] == -1 else float(sys.argv[6])  # ratio of txn to block inter-arrival times
total_txn_blks = 100 if len(sys.argv) < 8 or sys.argv[7] == -1 else int(sys.argv[7])  # total number of transactions and blocks to be generated
timeout = float('inf') if len(sys.argv) < 9 or sys.argv[8] == -1 else float(sys.argv[8])  # simulation timeout; set as None for now so need to Ctrl+C to end simulation
visualize = False if len(sys.argv) < 10 or sys.argv[9] == -1 else bool(int(sys.argv[9]))  # enable visualization

## Constants
initial_coins = 1000 ## change as needed

# Network speeds in Mbps
c_fast: int = 100 * 1024 * 1024
c_slow: int = 5 * 1024 * 1024
d_const: float = 96e-3

# Speed of light in s
rho_min: float = 10e-3
rho_max: float = 500e-3

# Transaction and block sizes in Mb
tx_size: float = 8 * 1024
block_max_size: int = 8 * 1024 * 1024

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

def exp_random_val(mean: float = 1.0):
    return np.random.exponential(mean)