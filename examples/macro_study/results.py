# this is a script to process the results of the case study (macro study of the database including several thousand activities)

import os
import pandas as pd
# make sure of the correct working directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)

# load data set
df_raw = pd.read_csv("data/results.csv", sep=";", index_col=None)
df = df_raw.copy()

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

for d in drop:
    df.drop(columns=[d], inplace=True)

# simplify the names of the activities
df.name = df.name.apply(lambda x: x.split(", ")[2])
print(df.name.unique())

# check for signigicant methods
grouped = df["score"].groupby(df["method_2"]).mean().sort_values(ascending=False)
print(grouped)

# # filter out methods where the maximum score < 0.01
df_sig = df.groupby("method_2").filter(lambda x: x["score"].abs().max() > 0.01)
grouped_sig = (
    df_sig["score"].groupby(df_sig["method_2"]).max().sort_values(ascending=False)
)
# print(grouped_sig)

df_sig.to_csv("data/results_significant.csv", sep=";")


# df_b = df[df.db_target == "Base"]
# df_p = df[df.db_target == "PkBudg500"]

# df_b.to_csv("data/results_base.csv", sep=";")
# df_p.to_csv("data/results_pk500.csv", sep=";")

df_w = df_sig[df_sig.method_1.str.contains("Waste")]
df_m = df_sig[df_sig.method_1.str.contains("Demand")]

m = df_m.method_1.unique()
w = df_w.method_1.unique()

df_w.to_csv("data/results_significant_waste.csv", sep=";")
df_m.to_csv("data/results_significant_material.csv", sep=";")
