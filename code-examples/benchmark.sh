#!/bin/bash -l

#SBATCH --job-name=julea_benchmark

# Define, how many nodes you need. Here, we ask for 1 node.
# Each node has 16 or 20 CPU cores.
#SBATCH --nodes=1

# Define which node to run on
#SBATCH --nodelist=ant17

# Make allocation to node exclusive
#SBATCH --exclusive

#              d-hh:mm:ss
#SBATCH --time=0-02:30:00

# Define the partition on which the job shall run. May be omitted.
#SBATCH --partition vl-parcio

# How much memory you need.
# --mem will define memory per node and
#SBATCH --mem=16GB    # Request all available memory on the node

# Run the job 10 times
#SBATCH --array=1-10

# Set output-dir
#SBATCH --output=benchmark-%j.out

# Set stderr
#SBATCH --error=benchmark-%j.err


. ./julea/scripts/environment.sh >> /dev/null

# Configure the JULEA
julea-config --user   --object-servers="$(hostname)" --kv-servers="$(hostname)" --db-servers="$(hostname)"   --object-backend=posix --object-path="/tmp/julea-$(id -u)/posix"   --kv-backend=lmdb --kv-path="/tmp/julea-$(id -u)/lmdb"   --db-backend=sqlite --db-path="/tmp/julea-$(id -u)/sqlite" >> /dev/null

# prepare the environment
./julea/scripts/setup.sh start-local >> /dev/null

# run the benchmark
./julea/scripts/benchmark.sh

# clean up the environment
./julea/scripts/setup.sh stop >> /dev/null