#!/bin/bash
# optional: write CSV header once
iters=5
z0=0.6
z1=0.6
outputfile_z0="results_z0.csv"
echo "z0,avg_slow,avg_fast,avg_high_cpu,avg_low_cpu,slow_contrib,fast_contrib,high_cpu_contrib,low_cpu_contrib" > "$outputfile_z0"

# initialize an array of 8 sums
sums=(0 0 0 0 0 0 0 0)

for ((i=1; i<=iters; i++)); do
    echo "Iteration $i: Running with z0=$z0 and z1=$z1"
    result=$(python3 x.py)  # expect: "v1,v2,...,v8"
    cleaned=$(echo "$result" | tr -d '[] ')
    IFS=',' read -r v1 v2 v3 v4 v5 v6 v7 v8 <<< "$cleaned"
    echo "Values: $v1, $v2, $v3, $v4, $v5, $v6, $v7, $v8"
    # accumulate
    sums[0]=$(echo "${sums[0]} + $v1" | bc -l)
    sums[1]=$(echo "${sums[1]} + $v2" | bc -l)
    sums[2]=$(echo "${sums[2]} + $v3" | bc -l)
    sums[3]=$(echo "${sums[3]} + $v4" | bc -l)
    sums[4]=$(echo "${sums[4]} + $v5" | bc -l)
    sums[5]=$(echo "${sums[5]} + $v6" | bc -l)
    sums[6]=$(echo "${sums[6]} + $v7" | bc -l)
    sums[7]=$(echo "${sums[7]} + $v8" | bc -l)
done

# compute averages
avgs=()
for s in "${sums[@]}"; do
    avgs+=( $(echo "$s / $iters" | bc -l) )
done

# write row to CSV (replace spaces with commas)
echo "$z0,${avgs[*]}" | sed 's/ /,/g' >> "$outputfile_z0"
