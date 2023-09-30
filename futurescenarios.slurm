#!/bin/bash

#SBATCH --job-name=FutureScenariosConsequential
#SBATCH --output=FutureScenariosConsequential_%j.out
#SBATCH --error=FutureScenariosConsequential_%j.err
#SBATCH --time=00:09:00
#SBATCH --mem=32GB
#SBATCH --partition=testing
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --mail-type=ALL
#SBATCH --mail-user=s.c.mcdowall@cml.leidenuniv.nl

module load python/3.10

# activate the virtual environment
source $HOME/data1/venvs/premise/bin/activate

# Your python script execution
python3.10 $HOME/gh/WasteAndMaterialFootprint/src/WasteAndMaterialFootprint/FutureScenariosConsequential.py