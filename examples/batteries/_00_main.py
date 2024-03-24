import subprocess
import os
from pathlib import Path
import shutil


from utils import *

# ************************************ USER SETTINGS ************************************
PROJECT = "TreX-premise-SSP2-cutoff"
KEY = "market for battery, Li-ion, rechargeable"

KEYWORDS_METHODS = [
    "ReCiPe 2016 v1.03, midpoint (I)",
    "EF v3.1 EN15804",
    "EDIP 2003 no LT",
    "Crustal Scarcity Indicator 2020",
    "T-reX",
]

DELETE_OLD_RAW_RESULTS = 0
DELETE_OLD_RAW_RESULTS_SC = 0

DELETE_OLD_PROCESSED_RESULTS = 0
DELETE_OLD_PROCESSED_RESULTS_SC = 0

DELETE_OLD_FIGURES = 0

SEARCH_ACTIVITIES = 0
SEARCH_METHODS = 0

GET_RESULTS = 0
GET_SUPPLY_CHAIN_RESULTS = 0

PROCESS_RESULTS = 1
PROCESS_SUPPLY_CHAIN_RESULTS = 1
DO_VISUALISATION = 1
DO_VISUALISATION_SUPPLY_CHAIN = 1
# ************************************ END USER SETTINGS ************************************
# Directory setup
CWD = Path.cwd()
DIR_DATA = CWD / "data"
DIR_VISUALISATION = CWD / "visualisation"

os.makedirs(DIR_DATA, exist_ok=True)
os.makedirs(DIR_VISUALISATION, exist_ok=True)

FILE_ACTIVITIES = DIR_DATA / "activities.csv"
FILE_METHODS = DIR_DATA / "methods.csv"

FILE_RESULTS = DIR_DATA / "raw_results.csv"
FILE_SUPPLYCHAIN_RESULTS = DIR_DATA / "raw_supply_chain_results.csv"

FILE_RESULTS_PROCESSED = DIR_DATA / "results_significant.csv"
FILE_RESULTS_PROCESSED_TOP_PROCESSES = (
    DIR_DATA / "results_significant_top_processes.csv"
)
FILE_RESULTS_PROCESSED_SC_1 = DIR_DATA / "results_significant_supply_chain.csv"
FILE_RESULTS_PROCESSED_SC_2 = (
    DIR_DATA / "results_significant_supply_chain_top_processes.csv"
)

if DELETE_OLD_RAW_RESULTS:
    os.remove(FILE_RESULTS) if os.path.exists(FILE_RESULTS) else None
if DELETE_OLD_RAW_RESULTS_SC:
    os.remove(FILE_SUPPLYCHAIN_RESULTS) if os.path.exists(
        FILE_SUPPLYCHAIN_RESULTS
    ) else None

if DELETE_OLD_PROCESSED_RESULTS:
    for file in [FILE_RESULTS_PROCESSED, FILE_RESULTS_PROCESSED_TOP_PROCESSES]:
        os.remove(file) if os.path.exists(file) else None

if DELETE_OLD_PROCESSED_RESULTS_SC:
    for file in [FILE_RESULTS_PROCESSED_SC_1, FILE_RESULTS_PROCESSED_SC_2]:
        os.remove(file) if os.path.exists(file) else None

if DELETE_OLD_FIGURES:
    shutil.rmtree(DIR_VISUALISATION, ignore_errors=True)

# List of script names
script_calculations = "_01a_calculate-batteries.py"
script_results = "_02a_process-results.py"
script_results_top_processes = "_02b_process-results_top-processes.py"
script_results_SC = "_03a_process-supply_chain_results.py"

# scripts_visualisation_bar = [
#     x for x in os.listdir() if x.endswith(".py") and "bar" in x
# ]
# scripts_visualisation_bar.sort()
scripts_visualisation_bar = [
    "_05a_visualisation_bar.py",
    "_05b_visualisation_bar_combine.py",
    "_05c_visualisation_bar_top-processes.py",
    "_05d_visualisation_bar_combine_top-processes.py",
]

# scripts_visualisation_scatter = [
#     x for x in os.listdir() if x.endswith(".py") and "scatter" in x
# ]
# scripts_visualisation_scatter.sort()

scripts_visualisation_scatter = [
    "_04a_visualisation_scatter.py",
    "_04b_visualisation_scatter_combine.py",
    "_04c_visualisation_scatter_similar_methods.py",
]


def run_script(script_name):
    try:
        # Run the script and wait for it to complete
        subprocess.run(["python", script_name], check=True)
    except subprocess.CalledProcessError as e:
        # If the script fails, print an error message
        print(
            f"\n+++++++++++++++++++++++\n\tERROR: {script_name}: \n\t\t{e}\n+++++++++++++++++++++++\n"
        )
        exit("Exiting...")


# Main execution logic
if __name__ == "__main__":
    if any([SEARCH_ACTIVITIES, SEARCH_METHODS, GET_RESULTS, GET_SUPPLY_CHAIN_RESULTS]):
        print("\n*******************************")
        print("\tRunning case study")
        print("*******************************")
        run_script(script_calculations)
    if PROCESS_RESULTS:
        print("*******************************")
        print("\tProcessing results")
        print("*******************************")
        run_script(script_results)
        print("*******************************")
        print("\tProcessing top processes results")
        print("*******************************")
        run_script(script_results_top_processes)
    if PROCESS_SUPPLY_CHAIN_RESULTS:
        print("*******************************")
        print("\tProcessing supply chain results")
        print("*******************************")
        run_script(script_results_SC)

    if DO_VISUALISATION:
        print("*******************************")
        print("\tVisualising results")
        print("*******************************")
        for script in scripts_visualisation_scatter:
            run_script(script)
    if DO_VISUALISATION_SUPPLY_CHAIN:
        print("*******************************")
        print("\tVisualising supply chain results")
        print("*******************************")
        for script in scripts_visualisation_bar:
            run_script(script)

    print("\n------------------------------------")
    print("\t\tDone!")
    print("------------------------------------\n")
