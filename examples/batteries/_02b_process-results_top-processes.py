# this is a script to process the contribution analysis results of the case study
import os
import numpy as np
import pandas as pd
import ast
from tabulate import tabulate

from _00_main import FILE_RESULTS_PROCESSED, FILE_RESULTS_PROCESSED_TOP_PROCESSES

DATA_FILE_IN = FILE_RESULTS_PROCESSED
DATA_FILE_OUT = FILE_RESULTS_PROCESSED_TOP_PROCESSES

# make sure of the correct working directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

pd.set_option("display.max_columns", 50)
pd.set_option("display.max_rows", 200)

# load data set
df_raw = pd.read_csv(DATA_FILE_IN, sep=";", index_col=None)
df = df_raw.copy().reset_index(drop=True)
df = df[df.method_0 == "T-reX"].reset_index(drop=True)

df["method_1"] = df["method_1"].apply(
    lambda x: (x[:32] + "[...]") if len(x) > 35 else x
)
df["method_2"] = df["method_2"].apply(
    lambda x: (x[:32] + "[...]") if len(x) > 35 else x
)


df["top_processes"] = df["top_processes"].apply(ast.literal_eval)
length_top = len(df["top_processes"][0])
length_top = 5
print(f"Number of top processes: {length_top}")

for i in range(length_top):
    df[f"tp_{i+1}"] = df["top_processes"].apply(lambda x: x[i])
    df[f"tp_{i+1}_score"] = df[f"tp_{i+1}"].apply(lambda x: x[0])
    # df[f"tp_{i+1}_demand"] = df[f"tp_{i+1}"].apply(lambda x: x[1])
    df[f"tp_{i+1}_name"] = df[f"tp_{i+1}"].apply(lambda x: x[2])
    # df[f"tp_{i+1}_location"] = df[f"tp_{i+1}"].apply(lambda x: x[3])
    df = df.drop(f"tp_{i+1}", axis=1)

df = df.drop("top_processes", axis=1)

cols_tp = [x for x in df.columns if "tp_" in x]
cols_tp_score = [x for x in cols_tp if "score" in x]
cols_tp_demand = [x for x in cols_tp if "demand" in x]
cols_tp_name = [x for x in cols_tp if "name" in x]

## DOESNT MAKE SENSE TO NORMALIZE THE SCORES WITH SOME OF THEM BEING NEGATIVE
# # Normalize the absolute values and retain the sign
# for col in cols_tp_score:
#     abs_normalized = abs(df[col]) / df[col].abs().sum()
#     df[col] = abs_normalized * df[col].apply(np.sign)


df.to_csv(DATA_FILE_OUT, sep=";", index=False)

print(f"Data processed. Shape: {df.shape}")
print(f"Saved data set: {DATA_FILE_OUT}")
