import matplotlib.pyplot as plt
import networkx as nx



# Example blockchain dictionary
blocks = {
    "Genesis": {"parent": None, "node": 0},
    "B1": {"parent": "Genesis", "node": 1},
    "B2": {"parent": "Genesis", "node": 2},
    "B3": {"parent": "B1", "node": 2},
    "B4": {"parent": "B2", "node": 1},
    "B5": {"parent": "B3", "node": 1},
}

# Build tree graph
G = nx.DiGraph()
for blk, info in blocks.items():
    if info["parent"]:
        G.add_edge(info["parent"], blk, node=info["node"])

# Assign colors per node (peer)
color_map = []
for node in G.nodes():
    if node == "Genesis":
        color_map.append("black")
    else:
        creator = blocks[node]["node"]
        if creator == 0: color_map.append("red")    # fast node
        elif creator == 1: color_map.append("blue") # slow node
        else: color_map.append("green")             # high CPU

# Draw tree
pos = nx.spring_layout(G)  # you can also try hierarchy layouts
nx.draw(G, pos, with_labels=True, node_color=color_map, node_size=800, font_size=8, arrows=True)

plt.title("Blockchain Tree Visualization")
plt.show()
# Save the figure
plt.savefig("blockchain_tree.png")


#things to do
# keep the number of nodes fixed
# 1. initial balance of each node 0

# 2. graphs
# vary interarrival time for fixed z0, z1 to observe trend in forks
#vary z0, z1 for fixed interarrival time to observe trend in forks

# 3. visualise blockchain
#code to visualise blockchain tree at the end of simulation

# 4. add command line parameters
#command line parameters to set n, z0, z1, interarrival time, timeout

# 5. comments in code
#comments in code

# 6. save blockchain to file
#store blockchain fo each node in a json file at the end

# 7. add time everywhere
# 8. report


# I have a ratio dictionary, which holds the ratio for each node
# now for a particular node I want to plot the ratio over z0, z1 values, essentially 