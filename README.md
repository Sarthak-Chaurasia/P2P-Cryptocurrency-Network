## CS765: Project Part - 1
# Simulation of a P2P Cryptocurrency Network

Team Members:  
Sarthak Chaurasia (22B1014)  
Mugdha Bilotia (22B1009)  
Svanik Gade (22B1004)

This directory contains the code for **HW1**, along with a design document and report.  

## Files Included
- **blockchain.py**: Contains the `Block` and `Blockchain` classes  
- **graph.py**: Builds the peer-to-peer (P2P) network with each node having between 3 and 6 neighbors  
- **transactions.py**: Contains `Transaction` class
- **main.py**: Main entry point to run the simulation  
- **nodes.py**: Contains the `Node` class  
- **modules.py**: Defines all simulation parameters and includes functions to generate random or exponentially distributed numbers. Contains default values of the parameters.
- **events.py**: Contains the `Event` and `Simulator` classes  

## Running the Simulation

The simulation is run using `main.py`. Parameters can be passed as command-line arguments to customize the behavior.  
If an argument is omitted or set to `-1`, its default value will be used.  

### Usage
```bash
python main.py [n] [z0] [z1] [T_tx] [T_interarrival] [txn_blk_ratio] [total_txn_blks] [timeout]
