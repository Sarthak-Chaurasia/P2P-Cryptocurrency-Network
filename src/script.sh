#!/bin/bash
# @sarthak change the values accordingly, and ek baar python main.py command dekhlena sahi likha h ki nahi
n=50
z1=0.6
z0=0.6
Tx=0.1
I=1
iters=5
# Tt_vals=(10 20 50 100)

z0_vals=(0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0)
z1_vals=(0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0)

outputfile_z0="results_z0.csv"
outputfile_z1="results_z1.csv"
outputfile_Tt="results_Tt.csv"

echo "z0,r1_high_cpu,r1_low_cpu,r1_fast,r1_slow,r2_high_cpu,r2_low_cpu,r2_fast,r2_slow" > "$outputfile_z0"

# For z0 values

for z0 in "${z0_vals[@]}"; do
    sums=(0 0 0 0 0 0 0 0)
    for ((i=1; i<=iters; i++)); do
        echo "Iteration $i: Running with z0=$z0 and z1=$z1"
        result=$(python3 main.py $n $z0 $z1 $Tx $I)
        cleaned=$(echo "$result" | tr -d '[] ')
        IFS=',' read -r v1 v2 v3 v4 v5 v6 v7 v8 <<< "$cleaned"
        sums[0]=$(echo "${sums[0]} + $v1" | bc -l)
        sums[1]=$(echo "${sums[1]} + $v2" | bc -l)
        sums[2]=$(echo "${sums[2]} + $v3" | bc -l)
        sums[3]=$(echo "${sums[3]} + $v4" | bc -l)
        sums[4]=$(echo "${sums[4]} + $v5" | bc -l)
        sums[5]=$(echo "${sums[5]} + $v6" | bc -l)
        sums[6]=$(echo "${sums[6]} + $v7" | bc -l)
        sums[7]=$(echo "${sums[7]} + $v8" | bc -l)
    done
    avgs=()
    for s in "${sums[@]}"; do
        avgs+=( $(echo "$s / $iters" | bc -l) )
    done
    echo "$z0,${avgs[*]}" | sed 's/ /,/g' >> "$outputfile_z0"
done

echo "z1,r1_high_cpu,r1_low_cpu,r1_fast,r1_slow,r2_high_cpu,r2_low_cpu,r2_fast,r2_slow" > "$outputfile_z1"

# For z1 values
z0=0.6
for z1 in "${z1_vals[@]}"; do
    sums=(0 0 0 0 0 0 0 0)
    for ((i=1; i<=iters; i++)); do
        echo "Iteration $i: Running with z0=$z0 and z1=$z1"
        result=$(python3 main.py $n $z0 $z1 $Tx $I)
        cleaned=$(echo "$result" | tr -d '[] ')
        IFS=',' read -r v1 v2 v3 v4 v5 v6 v7 v8 <<< "$cleaned"
        sums[0]=$(echo "${sums[0]} + $v1" | bc -l)
        sums[1]=$(echo "${sums[1]} + $v2" | bc -l)
        sums[2]=$(echo "${sums[2]} + $v3" | bc -l)
        sums[3]=$(echo "${sums[3]} + $v4" | bc -l)
        sums[4]=$(echo "${sums[4]} + $v5" | bc -l)
        sums[5]=$(echo "${sums[5]} + $v6" | bc -l)
        sums[6]=$(echo "${sums[6]} + $v7" | bc -l)
        sums[7]=$(echo "${sums[7]} + $v8" | bc -l)
    done
    avgs=()
    for s in "${sums[@]}"; do
        avgs+=( $(echo "$s / $iters" | bc -l) )
    done
    echo "$z1,${avgs[*]}" | sed 's/ /,/g' >> "$outputfile_z1"
done