import subprocess
import os
from pathlib import Path
import shutil

# ************************************ USER SETTINGS ************************************
PROJECT = "TreX-Premise-SSP2-cutoff"
KEY = "market for battery, Li-ion, rechargeable"

KEYWORDS_METHODS = [
    "ReCiPe 2016 v1.03, midpoint (I)",
    "EF v3.1 EN15804",
    "EDIP 2003 no LT",
    "Crustal Scarcity Indicator 2020",
    "T-reX",
]

DELETE_OLD_RESULTS = 1
DELETE_OLD_FIGURES = 1
SEARCH_ACTIVITIES = 1
SEARCH_METHODS = 1
GET_RESULTS = 1
GET_SUPPLY_CHAIN_RESULTS = 0
DO_VISUALISATION = 1
DO_VISUALISATION_SUPPLY_CHAIN = 0
# ************************************ END USER SETTINGS ************************************
# Directory setup
CWD = Path.cwd()
DIR_DATA = CWD / "data"
DIR_VISUALISATION = CWD / "visualisation"

if DELETE_OLD_RESULTS:
    shutil.rmtree(DIR_DATA, ignore_errors=True)
if DELETE_OLD_FIGURES:
    shutil.rmtree(DIR_VISUALISATION, ignore_errors=True)

os.makedirs(DIR_DATA, exist_ok=True)
os.makedirs(DIR_VISUALISATION, exist_ok=True)

FILE_ACTIVITIES = DIR_DATA / "activities.csv"
FILE_METHODS = DIR_DATA / "methods.csv"
FILE_RESULTS = DIR_DATA / "results.csv"
FILE_SUPPLYCHAINRESULTS = DIR_DATA / "supply_chain_results.csv"

# List of script names
script_calculations = "_01_calculate-batteries.py"
script_results = "_02_process-results.py"
script_results_top_processes = "_02b_process-results_top-processes.py"
script_results_SC = "_03_process-supply_chain_results.py"

scripts_visualisation_bar = [
    x for x in os.listdir() if x.endswith(".py") and "bar" in x
]
scripts_visualisation_scatter = [
    x for x in os.listdir() if x.endswith(".py") and "scatter" in x
]


def run_script(script_name):
    try:
        # Run the script and wait for it to complete
        subprocess.run(["python", script_name], check=True)
    except subprocess.CalledProcessError as e:
        # If the script fails, print an error message
        print(f"An error occurred while executing {script_name}: {e}")


# Main execution logic
if __name__ == "__main__":
    if SEARCH_ACTIVITIES or SEARCH_METHODS:
        run_script(script_calculations)
    if GET_RESULTS or GET_SUPPLY_CHAIN_RESULTS:
        run_script(script_results)

    if DO_VISUALISATION:
        for script in scripts_visualisation_scatter:
            run_script(script)
    if DO_VISUALISATION_SUPPLY_CHAIN:
        for script in scripts_visualisation_bar:
            run_script(script)
