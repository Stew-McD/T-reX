


## To separate the waste and material methods

# df_w = df_sig[df_sig.method_1.str.contains("Waste")]
# df_m = df_sig[df_sig.method_1.str.contains("Demand")]

# m = df_m.method_1.unique()
# w = df_w.method_1.unique()


# df_w.to_csv("data/results_significant_waste.csv", sep=";")
# df_m.to_csv("data/results_significant_material.csv", sep=";")
