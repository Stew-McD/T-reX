# this is a script to process the contribution analysis results of the case study
import os
import numpy as np
import pandas as pd

# make sure of the correct working directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

pd.set_option("display.max_columns", 50)
pd.set_option("display.max_rows", 200)

# load data set
df_raw = pd.read_csv("data/supply_chain_results.csv", sep=";", index_col=None)
df = df_raw.copy().reset_index(drop=True)

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
    'key',
    'database',
    'product',
        
]

for d in drop:
    df.drop(columns=[d], inplace=True, errors="ignore")


# simplify the names of the activities
df.name = df.name.apply(lambda x: x.split(", ")[2])
print(df.name.unique())

# check for signigicant methods
grouped = df["total"].groupby(df["method_2"]).mean().sort_values(ascending=False)

# # filter out methods where the maximum score < 0.01
df_sig = df.groupby("method_2").filter(lambda x: x["total"].abs().max() > 0.01)
grouped_sig = (
    df_sig["total"].groupby(df_sig["method_2"]).max().sort_values(ascending=False)
)
df_sig.to_csv("data/supply_chain_results_significant.csv", sep=";")

total_col_index = df.columns.get_loc("total")

# Process each row
for index, row in df_sig.iterrows():
    # Sort values in descending order after 'total' column
    sorted_row = row.iloc[total_col_index + 1:].sort_values(ascending=False)

    # Take top 5 values
    top_5_cols = sorted_row.head(5)
    other_cols = sorted_row.iloc[5:]

    # Update the DataFrame for top 5 columns
    for col in top_5_cols.index:
        df_sig.at[index, col] = top_5_cols[col]

    for col in other_cols.index:
        df_sig.at[index, col] = 0.0
        
    df_sig.at[index, 'other'] = 1.0 - sum(top_5_cols)
    

df_sig.reset_index(drop=True, inplace=True)
df_sig.to_csv("data/supply_chain_results_significant_ranked.csv", sep=";", index=False)