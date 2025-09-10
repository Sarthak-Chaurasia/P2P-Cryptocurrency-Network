import pandas as pd
import matplotlib.pyplot as plt

# Read CSV file
# change z0 to z0 to get for z0
df = pd.read_csv("results_z0.csv")  # Replace with your actual CSV filename

# Plot for r1
plt.figure(figsize=(8, 6))
plt.plot(df["z0"], df["r1_high_cpu"], label="R1 High CPU", marker="o")
plt.plot(df["z0"], df["r1_low_cpu"], label="R1 Low CPU", marker="s")
plt.xlabel("z0")
plt.ylabel("CPU")
plt.title("z0 vs R1 High CPU / Low CPU")
plt.legend()
plt.grid(True)
plt.savefig("0.1_z0_r1_high_low_cpu.png")
plt.show()

plt.figure(figsize=(8, 6))
plt.plot(df["z0"], df["r1_fast"], label="R1 Fast", marker="o")
plt.plot(df["z0"], df["r1_slow"], label="R1 Slow", marker="s")
plt.xlabel("z0")
plt.ylabel("Values")
plt.title("z0 vs R1 Fast / Slow")
plt.legend()
plt.grid(True)
plt.savefig("0.1_z0_r1_fast_slow.png")
plt.show()

# Plot for r2
plt.figure(figsize=(8, 6))
plt.plot(df["z0"], df["r2_high_cpu"], label="R2 High CPU", marker="o")
plt.plot(df["z0"], df["r2_low_cpu"], label="R2 Low CPU", marker="s")
plt.xlabel("z0")
plt.ylabel("CPU")
plt.title("z0 vs R2 High CPU / Low CPU")
plt.legend()
plt.grid(True)
plt.savefig("0.1_z0_r2_high_low_cpu.png")
plt.show()

plt.figure(figsize=(8, 6))
plt.plot(df["z0"], df["r2_fast"], label="R2 Fast", marker="o")
plt.plot(df["z0"], df["r2_slow"], label="R2 Slow", marker="s")
plt.xlabel("z0")
plt.ylabel("Values")
plt.title("z0 vs R2 Fast / Slow")
plt.legend()
plt.grid(True)
plt.savefig("0.1_z0_r2_fast_slow.png")
plt.show()
