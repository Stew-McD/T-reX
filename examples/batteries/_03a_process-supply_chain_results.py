# this is a script to process the contribution analysis results of the case study
import os
import numpy as np
import pandas as pd

from utils import replace_string_in_df, term_replacements
from _00_main import FILE_SUPPLYCHAIN_RESULTS, FILE_RESULTS_PROCESSED_SC_1, FILE_RESULTS_PROCESSED_SC_2
# make sure of the correct working directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

pd.set_option("display.max_columns", 50)
pd.set_option("display.max_rows", 200)

# load data set
DATA_FILE_IN = FILE_SUPPLYCHAIN_RESULTS
DATA_FILE_OUT_1 = FILE_RESULTS_PROCESSED_SC_1
DATA_FILE_OUT_2 = FILE_RESULTS_PROCESSED_SC_2

# load data set
df_raw = pd.read_csv(DATA_FILE_IN, sep=";", index_col=None)
df = df_raw.copy().reset_index(drop=True)

# Call the function with the DataFrame and the replacements dictionary
for term, replacement in term_replacements.items():
    df_raw = replace_string_in_df(df, term_replacements)

# filter out unnecessary columns
df = df[df.database != "ecoinvent-3.9.1-cutoff"]
drop = [
    "db_model",
    "db_version",
    "db_system",
    "db_base",
    "code",
    "db_ssp",
    "direct emissions",
    "location",
    "key",
    "database",
    "product",
]

for d in drop:
    df = df.drop(columns=[d], errors="ignore")


# simplify the names of the activities
df.name = df.name.apply(lambda x: x.split(", ")[2])
print(df.name.unique())
df["method_1"] = df["method_1"].apply(
    lambda x: (x[:32] + "[...]") if len(x) > 35 else x
)
df["method_2"] = df["method_2"].apply(
    lambda x: (x[:32] + "[...]") if len(x) > 35 else x
)

# check for signigicant methods
grouped = df["total"].groupby(df["method_2"]).mean().sort_values(ascending=False)

# # filter out methods where the maximum score < 0.01
df_sig = df.groupby("method_2").filter(lambda x: x["total"].abs().max() > 0.01)
grouped_sig = (
    df_sig["total"].groupby(df_sig["method_2"]).max().sort_values(ascending=False)
)
df_sig.to_csv(DATA_FILE_OUT_1, sep=";")
print(f"Data processed. Shape: {df_sig.shape}")
print(f"Saved data set: {DATA_FILE_OUT_1}")

total_col_index = df.columns.get_loc("total")

# Process each row
for index, row in df_sig.iterrows():
    # Sort values in descending order after 'total' column
    sorted_row = row.iloc[total_col_index + 1 :].sort_values(ascending=False)

    # Take top 5 values
    top_5_cols = sorted_row.head(5)
    other_cols = sorted_row.iloc[5:]

    # Update the DataFrame for top 5 columns
    for col in top_5_cols.index:
        df_sig.at[index, col] = top_5_cols[col]

    for col in other_cols.index:
        df_sig.at[index, col] = 0.0

    df_sig.at[index, "other"] = 1.0 - sum(top_5_cols)


df_sig.reset_index(drop=True, inplace=True)
df_sig.to_csv(DATA_FILE_OUT_2, sep=";", index=False)

print(f"Data processed. Shape: {df_sig.shape}")
print(f"Saved data set: {DATA_FILE_OUT_2}")
