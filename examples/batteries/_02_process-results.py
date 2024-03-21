# this is a script to process the results of the case study, easy to adapt to other case studies

import os
import pandas as pd

# make sure of the correct working directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)

# load data set
DATA_FILE = "data/results.csv"
DATA_FILE_OUT = "data/results_significant.csv"

print(f"Loading data set: {DATA_FILE}")
df_raw = pd.read_csv(DATA_FILE, sep=";", index_col=None)
df = df_raw.copy()

print(f"Data set loaded. Shape: {df.shape}")
print(f"Columns: \n{df.columns.values}")
print("Processing data...")
# filter out unnecessary columns
df = df[df.database != "ecoinvent-3.9.1-cutoff"]
drop = [
    "db_model",
    "db_version",
    "db_system",
    "db_base",
    "code",
    "db_ssp",
    "database",
]

print(f"Filtering out columns: {drop}")
for d in drop:
    df.drop(columns=[d], inplace=True)

# simplify the names of the activities
df.name = df.name.apply(lambda x: x.split(", ")[2])

# check for signigicant methods
grouped = df["score"].groupby(df["method_2"]).mean().sort_values(ascending=False)

# # filter out methods where the maximum score < 0.01
MIN_SCORE = 0.01
print(f"Filtering out methods where the maximum score < {MIN_SCORE}")
df_sig = df.groupby("method_2").filter(lambda x: x["score"].abs().max() > MIN_SCORE)
grouped_sig = (
    df_sig["score"].groupby(df_sig["method_2"]).max().sort_values(ascending=False)
)

print(f"Data processed. Shape: {df_sig.shape}")
print(f"Columns: \n{df_sig.columns.values}")
print(f"Number of unique methods: {len(df_sig.method_2.unique())}")
print(f"Number of unique activities: {len(df_sig.name.unique())}")
print(f'Saving results to {DATA_FILE_OUT}"')
df_sig.to_csv(DATA_FILE_OUT, sep=";", index=False)


## To separate the T-reX methods

# df_w = df_sig[df_sig.method_1.str.contains("Waste")]
# df_m = df_sig[df_sig.method_1.str.contains("Demand")]

# m = df_m.method_1.unique()
# w = df_w.method_1.unique()


# df_w.to_csv("data/results_significant_waste.csv", sep=";")
# df_m.to_csv("data/results_significant_material.csv", sep=";")
