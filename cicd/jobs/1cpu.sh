#!/bin/bash -l
#SBATCH --job-name="montecarlo-cpu"
#SBATCH -N 1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=128
#SBATCH --output=mcs-cpu.%J.out
#SBATCH --error=mcs-cpu.%J.err
#SBATCH -p cpu
#SBATCH -q default
#SBATCH --time=48:00:00
#SBATCH --constraint=cpuonly
#SBATCH -A LXP

# move back to root directory
cd ..

# set the current datetime
DATE_WITH_TIME=`date "+%Y%m%d-%H%M%S"`

module load Python
#module load gnuplot/5.4.2-GCCcore-10.3.0gnuplot/5.4.2-GCCcore-10.3.0
pip install virtualenv
virtualenv 1cpu128c

source 1cpu128c/bin/activate
pip install -r requirements.txt

## Generate the list of core used several times
#my_list_of_core="1 2 $(seq 20 40 80 100 128)"

my_list_of_core="20 40 80 100 128"

for nb_core in $my_list_of_core;  ## it generates a sequence: 1 2 10 .. 120 128
    do srun -c $nb_core python mcs-cpu.py >> $nb_core.log
done


## PostProcessing (parse and aggregate outputs)
for post_process_file in $my_list_of_core;  ## it generates a sequence: 1 2 10 .. 120 128
    ## Here we extract second line of each XXX.log file and put it in another with 'Append' mode
	do parse_output=$(sed -n '2p' < $post_process_file.log) 
	echo "$post_process_file $parse_output" >> post_process.$DATE_WITH_TIME.log
    # delete individual log file
    rm -f $post_process_file.log
done

## Plot post_process.log (you can then postprocess with whatever you want ^^)
#gnuplot
#set term png  
#set output "scalability.png"
#plot "post_process.log" using 2: xtic(1) with histogram
#quit

printenv | grep SLURM
