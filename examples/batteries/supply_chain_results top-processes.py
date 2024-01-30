# this is a script to process the contribution analysis results of the case study
import os
import numpy as np
import pandas as pd
import ast
from tabulate import tabulate

# make sure of the correct working directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

pd.set_option("display.max_columns", 50)
pd.set_option("display.max_rows", 200)

# load data set
df_raw = pd.read_csv("data/results_significant.csv", sep=";", index_col=None)
df = df_raw.copy().reset_index(drop=True)
df = df[df.method_0 == "WasteAndMaterialFootprint"].reset_index(drop=True)


df["top_processes"] = df["top_processes"].apply(ast.literal_eval)
length_top = len(df["top_processes"][0])
length_top = 5

for i in range(length_top):
    df[f"tp_{i+1}"] = df["top_processes"].apply(lambda x: x[i])
    df[f"tp_{i+1}_score"] = df[f"tp_{i+1}"].apply(lambda x: x[0])
    # df[f"tp_{i+1}_demand"] = df[f"tp_{i+1}"].apply(lambda x: x[1])
    df[f"tp_{i+1}_name"] = df[f"tp_{i+1}"].apply(lambda x: x[2])
    # df[f"tp_{i+1}_location"] = df[f"tp_{i+1}"].apply(lambda x: x[3])
    df.drop(f"tp_{i+1}", axis=1, inplace=True)

df.drop("top_processes", axis=1, inplace=True)

cols_tp = [x for x in df.columns if "tp_" in x]
cols_tp_score = [x for x in cols_tp if "score" in x]
cols_tp_demand = [x for x in cols_tp if "demand" in x]
cols_tp_name = [x for x in cols_tp if "name" in x]

## DOESNT MAKE SENSE TO NORMALIZE THE SCORES WITH SOME OF THEM BEING NEGATIVE
# # Normalize the absolute values and retain the sign
# for col in cols_tp_score:
#     abs_normalized = abs(df[col]) / df[col].abs().sum()
#     df[col] = abs_normalized * df[col].apply(np.sign)


df.to_csv("data/top-processes.csv", sep=";", index=False)

