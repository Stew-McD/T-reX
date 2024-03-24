# this is a script to process the results of the case study, easy to adapt to other case studies

import os
import pandas as pd

from _00_main import FILE_RESULTS, FILE_RESULTS_PROCESSED
from utils import replace_string_in_df, term_replacements

# make sure of the correct working directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)

# load data set
DATA_FILE_IN = FILE_RESULTS
DATA_FILE_OUT = FILE_RESULTS_PROCESSED

MIN_SCORE = 10^(-6)


print(f"Loading data set: {DATA_FILE_IN}")
df_raw = pd.read_csv(DATA_FILE_IN, sep=";", index_col=None)
df = df_raw.copy()

# Call the function with the DataFrame and the replacements dictionary
for term, replacement in term_replacements.items():
    df_raw = replace_string_in_df(df, term_replacements)

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
    df = df.drop(columns=[d], errors="ignore")


# simplify the names of the activities
df.name = df.name.apply(lambda x: x.split(", ")[2])

df = df.assign(method_1=df["method_1"].apply(
    lambda x: (x[:32] + "[...]") if len(x) > 35 else x
))
df = df.assign(method_2=df["method_2"].apply(
    lambda x: (x[:32] + "[...]") if len(x) > 35 else x
))


# check for signigicant methods
grouped = df["score"].groupby(df["method_2"]).mean().sort_values(ascending=False)

# # filter out methods where the maximum score is less than a certain value
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
