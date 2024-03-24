
# imports
import sys
from bw2analyzer.tagged import recurse_tagged_database
import bw2data as bd
import pandas as pd
import plotly.graph_objects as go
import copy
import numpy as np
import ast
import bw2io as bi
import bw2calc as bc

from _00_main import (
    PROJECT,
    KEY,
    KEYWORDS_METHODS,
    SEARCH_ACTIVITIES,
    SEARCH_METHODS,
    GET_RESULTS,
    GET_SUPPLY_CHAIN_RESULTS,
    FILE_ACTIVITIES,
    FILE_METHODS,
    FILE_RESULTS,
    FILE_SUPPLYCHAIN_RESULTS,
)


sys.setrecursionlimit(30000)  # or a higher value

# %% [markdown]
# ## Create example database

# %% [markdown]
# First, let's create an arbitrary brightway2 database that we will visualize in the next steps.

# %%
# create example database
project = "default"  # make sure to choose a project that has a biosphere!
db_name = "ecoinvent-3.9.1-cutoff"

bd.projects.set_current(project)
CO2 = bw.Database("biosphere3").search("Carbon dioxide, fossil")[0].key


# %% [markdown]
# Before we can draw a sankey diagram, we need to collect the necessary data and format it in a way that plotly understands. Data collection has four steps:
#
# 1) define functional unit and method
#
# 2) use brightway2's built-in method `recurse_tagged_database` to collect lcia data of our functional unit and it's upstream supply chains
#
# 3) use a custom routine to convert the returned data structure (nested format) into a dataframe (flat format)
#
# 4) manually add biosphere information, which is not returned by `recurse_tagged_database`


# get methods and activities
db = bd.Database(db_name)
activities = pd.read_csv(FILE_ACTIVITIES, sep=";")
activities = activities[activities.database == db_name]
activities["activity_object"] = activities.key.apply(
        lambda x: bd.get_activity(ast.literal_eval(x))
    )
methods = pd.read_csv(FILE_METHODS, sep=";")
methods = methods["tuple"].apply(ast.literal_eval).to_list()

act = activities.activity_object.iloc[0]
method = methods[0]
print(f"method: {method}")
print(f"activity: {act}")

# ### Get nested data

def get_nested_graph(act, method):
    # traverse graph and get LCIA contributions
    functional_unit = {act: 1}
    lca = bc.LCA(functional_unit, method)
    lca.lci(factorize=True)
    lca.lcia()
    method_dict = {o[0]: o[1] for o in bd.Method(method).load()}
    return recurse_tagged_database(act, 1, method_dict, lca, "tag", "other")


graph = get_nested_graph(act, method)
graph

# %% [markdown]
# ### Convert to flat format


# %%
def flatten(graph, as_dataframe=True):
    # nested graph to flat list

    def flatten_recursive(graph, target=None, agg=0):
        if "activity" in graph:
            d = graph["activity"]._data
        else:
            d = {"type": "biosphere"}
        d["location"] = d.get("location")
        d["tag"] = graph["tag"]
        d["type"] = d.get("type", "technosphere")
        d["source"] = len(flat_list)
        d["target"] = target
        d["amount"] = graph["amount"]
        d["impact"] = graph["impact"]
        flat_list.append(d)
        for ex in graph.get("biosphere", []) + graph.get("technosphere", []):
            agg += flatten_recursive(ex, target=d["source"])
        d["value"] = agg + d["impact"]
        return d["value"]

    flat_list = []
    flatten_recursive(graph)

    if as_dataframe is True:
        df = pd.DataFrame(flat_list).convert_dtypes({"target": pd.Int64Dtype})
        return df
    else:
        return flat_list


df = flatten(graph, as_dataframe=True)
df

# %% [markdown]
# As we can see, above table contains "NA" entries, in the rows that describe biosphere flows. This is because brightway2 does not currently provide the corresponding information. Let's try to fill it in manually.

# %% [markdown]
# ### Fill in missing biosphere data
#
# Fossil CO2 is the only biosphere flow present in our example database. Hence, it is easy to provide the missing information. Note that it is currently not possible to distinguish between different biosphere flows in the output returned by `recurse_tagged_database`.

# %%
act = bw.get_activity(CO2)._data
df["name"].fillna(act["name"], inplace=True)
df["unit"].fillna(act["unit"], inplace=True)
df["database"].fillna(act["database"], inplace=True)
df["code"].fillna(act["code"], inplace=True)
df["location"].fillna(", ".join(act["categories"]), inplace=True)
df

# %% [markdown]
# ## Draw sankey graph
#
# Now that the data is complete and in the right format, we can draw a sankey diagram! For this, we use a custom routine `make_sankey`, which accepts the formatted dataframe, as well as two functions: `label_func` accepts a row from the dataframe and returns the node label, which will appear in the sankey diagram. `node_color_func` accepts a row and returns the color of the sankey node. Per default, labels contain the name, location and unit of the activity. The node color is grey for technosphere activities and green for biosphere activities. Note that there is no option to change the link colors: they are used to indicate positive (blue) versus negative (red) flows.


# %%
def make_labels(row):
    # return node label for a given dataframe row
    # note that values can be iterable!
    name = (
        ",".join(row["name"])
        if type(row["name"]) in [np.ndarray, list]
        else row["name"]
    )
    location = (
        ",".join(row["location"])
        if type(row["location"]) in [np.ndarray, list]
        else row["location"]
    )
    unit = (
        ",".join(row["unit"])
        if type(row["unit"]) in [np.ndarray, list]
        else row["unit"]
    )
    return f"{location}<br>{name}<br>{unit}"


def make_node_color(row):
    # return node color for a given dataframe row
    # note that values can be iterable!
    if type(row["type"]) in [list, np.ndarray]:
        if all([r == "biosphere" for r in row["type"]]):
            return "rgba(0,150,0,0.6)"
        else:
            return "rgba(0,0,0,0.6)"
    else:
        if row["type"] == "biosphere":
            return "rgba(0,150,0,0.6)"
        else:
            return "rgba(0,0,0,0.6)"


def make_sankey(df, label_func=make_labels, node_color_func=make_node_color):
    # use plotly to create a sankey diagram of a dataframe with columns source, target, value, label, node color

    df = df.copy()

    # deal with plotly weirdness: make sure source and target are ints
    id_map = {
        v: i for i, v in enumerate(df["target"].append(df["source"]).dropna().unique())
    }
    df["source"] = df["source"].map(id_map)
    df["target"] = df["target"].map(id_map)
    df = df.sort_values("source").reset_index(drop=True)

    # make sure negative values are drawn in different color
    df_ = df.dropna(subset=["source", "target"]).copy()
    df_["isNegative"] = df_["value"] < 0
    df_["edge color"] = [
        "rgba(255,100,100,0.3)" if neg else "rgba(100,100,255,0.3)"
        for neg in df_["isNegative"]
    ]
    df_["value"] = df_["value"].abs()

    # add label and node color columns
    for i, row in df.iterrows():
        df.loc[i, "label"] = label_func(row)
        df.loc[i, "node color"] = node_color_func(row)

    # do the drawing
    fig = go.Figure(
        data=[
            go.Sankey(
                node=dict(
                    pad=100,
                    label=df["label"].astype(str).values,
                    color=df["node color"].values,
                ),
                link=dict(
                    source=df_["source"].values,
                    target=df_["target"].values,
                    value=df_["value"].values,
                    color=df_["edge color"].values,
                ),
            )
        ]
    )

    return fig


fig = make_sankey(df)
fig

# %% [markdown]
# ## Manipulate the sankey graph

# %% [markdown]
# In this section, we will see how to manipulate the sankey graph. For this, we use a custom routine `group_nodes`. It accepts a column name `by`, whose values are used to group the sankey nodes, and returns a new dataframe containing the aggregated data. The function further makes sure that all links are updated, so that the aggregated nodes remain in the right place.


# %%
def group_nodes(df, by, propagate=True):
    # combine nodes based on a given column "by"

    def group(df, by, agg_dict):
        # group
        df2 = df.groupby([by, "target"], as_index=False, dropna=False).agg(agg_dict)
        # make sure all links are updated to reflect new node ids
        id_map = pd.Series(
            {i: s for s in df2["source"].values for i in s.split(", ") if i}
        )
        df2["target"] = df2["target"].astype(str).map(id_map).fillna(df2["target"])
        return df2

    # copy df
    df2 = df.copy()

    # define how to aggregate columns
    default_aggregation = lambda x: list(pd.unique(np.array(list(x)).flatten()))
    agg_dict = {c: default_aggregation for c in df.columns if c not in ["target", by]}
    agg_dict["value"] = sum
    agg_dict["source"] = lambda x: ", ".join(pd.unique([str(e) for e in x]))

    # do repetitive grouping until length of df does not change anymore
    old_len = len(df)
    new_len = len(df) - 1
    while new_len < old_len:
        old_len = len(df2)
        df2 = group(df2, by, agg_dict)
        new_len = len(df2)
        if propagate is False:
            break

    return df2


# %% [markdown]
# For starters, let's use the function to aggregate nodes that have the same `location`. Note: the function will only aggregate nodes, which have the same target. This makes sure that the sankey graph remains intact.

# %%
# group by location
df2 = group_nodes(df, by="location").reset_index(drop=True)
df2

# %% [markdown]
# Comparing this dataframe to the original, `df`, We see that the two nodes B and C were aggregated into one. Let's draw the new frame:

# %%
make_sankey(df2)

# %% [markdown]
# Next, let's aggregate by database.

# %%
make_sankey(group_nodes(df, "database"))

# %% [markdown]
# We can also create new columns to group by them. For example, we can group positive and negative flows together:

# %%
df["tag"] = df["value"] < 0
make_sankey(group_nodes(df, by="tag"))

# %% [markdown]
# New columns allow us to define arbitrary grouping criteria. For example, we might want to explicitly merge two nodes (note that they must have the same target!). Let's aggregate E and G into one:

# %%
df["tag"] = df["name"].apply(lambda n: n if n not in ["E", "G"] else "E")
make_sankey(group_nodes(df, by="tag"))

# %% [markdown]
# We can also manipulate the data in other ways than grouping. For example, we can drop all flows, which are below a certain threshold:

# %%
make_sankey(df[df["value"].abs() >= 0.7])

# %% [markdown]
# You can use all pandas operations to manipulate the dataframe. Feel free to play around until you have the sankey graph you like!
