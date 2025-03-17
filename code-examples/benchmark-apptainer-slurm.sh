#!/bin/bash -l

#SBATCH --job-name=julea_benchmark

# Define which node to run on
##SBATCH --nodelist=ant17

#SBATCH --constraint=epyc3

# Make allocation to node exclusive
#SBATCH --exclusive

#              d-hh:mm:ss
#SBATCH --time=0-2:30:00

# Define the partition on which the job shall run. May be omitted.
#SBATCH --partition vl-parcio

# How much memory you need.
# --mem will define memory per node and
#SBATCH --mem=16GB 

# Run the job 10 times
#SBATCH --array=1-10

# Set output-dir
#SBATCH --output=./res/apptainer/benchmark-%a.out

# Set stderr
#SBATCH --error=./res/apptainer/benchmark-%a.err

srun apptainer exec --bind .:/mnt/ --bind /tmp:/tmp ../apptainer-test.sif /mnt/benchmark-apptainer.sh&
wait