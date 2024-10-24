#!/bin/bash -l
#SBATCH --job-name="montecarlo 1 gpu node"
#SBATCH -N 1
#SBATCH --ntasks=4
#SBATCH --ntasks-per-node=4
#SBATCH --gpus-per-task=1
#SBATCH --output=mcs-gpu.%J.out
#SBATCH --error=mcs-gpu.%J.err
#SBATCH -p gpu
#SBATCH -q default
#SBATCH --time=05:00:00
#SBATCH -A LXP

# move back to root directory
cd ..

# set the current datetime
DATE_WITH_TIME=`date "+%Y%m%d-%H%M%S"`

module load Python CUDA
#module load gnuplot/5.4.2-GCCcore-10.3.0gnuplot/5.4.2-GCCcore-10.3.0
pip install virtualenv
virtualenv 1gpu

source 1gpu/bin/activate
pip install -r requirements.txt


# run the mcs-gpu.py and capture the running time to log file
python mcs-gpu.py >> 1gpu.$DATE_WITH_TIME.log

printenv | grep SLURM
