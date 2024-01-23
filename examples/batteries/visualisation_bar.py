import matplotlib.pyplot as plt
import pandas as pd
import os
import matplotlib as mpl
from matplotlib.lines import Line2D
import scienceplots
from tqdm import tqdm
import seaborn as sns
import random

# Set a fixed figure size to match your largest plot (274x343 pixels)
fixed_figsize = (250 / 100, 500 / 100)  # Convert pixels to inches

plt.rcParams["figure.figsize"] = fixed_figsize
plt.rcParams["figure.autolayout"] = False


# set global formatting options
rc_fonts = {
    "font.family": "serif",
    "text.usetex": True,
    "text.latex.preamble": "\n".join(
        [
            "\\usepackage{libertine}",
            "\\usepackage[libertine]{newtxmath}",
        ]
    ),
}
mpl.style.use(["science"])
mpl.rcParams.update(rc_fonts)


# Define the function to replace strings in the DataFrame
def replace_string_in_df(df, term, replacement):
    df = df.replace(term, replacement)
    return df


# Define the function to replace strings in a string
def replace_strings_in_string(string, term_replacements):
    for term, replacement in term_replacements.items():
        string = string.replace(term, replacement)
    return string


# Read in the data
df_raw = pd.read_csv(
    "data/supply_chain_results_significant_ranked.csv", sep=";", index_col=None
)

# Apply string replacements to the DataFrame
term_replacements = {
    "cubic meter": r"m$^{3}$",
    "m3": r"m$^{3}$",
    "(": " (",
    "kilogram": "kg",
    "kgCO2eq": "kg CO$_{2}$ eq",
    "kg CO2 eq": "kg CO$_{2}$ eq",
    "kg CO2-eq": "kg CO$_{2}$ eq",
    "kilowatt hour": "kWh",
    "Carbondioxide": "Carbon dioxide",
    "Naturalgas": "Natural gas",
    "square meter": "m$^{2}$",
}

for term, replacement in term_replacements.items():
    replace_string_in_df(df_raw, term, replacement)

# Aggregate the methods into a single column
method_full = list(zip(df_raw["method_0"], df_raw["method_1"], df_raw["method_2"]))
df_raw.insert(0, "method_full", method_full)

# # Define the plotting colors
# color_palette = [
#     "#FF5733", "#3B9C9C", "#FFC300", "#FF6363", "#4CAF50",
#     "#9C27B0", "#2196F3", "#F44336", "#FFEB3B", "#673AB7",
#     "#009688", "#795548", "#00BCD4", "#E91E63", "#FF7043",
#     "#4CAF50", "#FF9800", "#607D8B", "#9C27B0", "#3F51B5",
#     "#E91E63", "#FFC107", "#8BC34A", "#2196F3", "#FF5722",
#     "#00BCD4", "#FF5252", "#536DFE", "#FF9800", "#9E9E9E",
#     "#8BC34A", "#FF5722", "#00BCD4", "#FF5252", "#536DFE",
#     "#FF9800", "#9E9E9E", "#8BC34A", "#FF5722", "#00BCD4"
# ]


# colors = list(set(colors))

activities = df_raw["name"].unique()
methods_full = df_raw["method_full"].unique()
scenarios = df_raw["db_target"].unique()


start_col = df_raw.columns.get_loc("total") + 1

df = df_raw.copy().reset_index(drop=True)
# filter out unnecessary columns

col_sums = df.iloc[:, start_col:].sum()
sorted_cols = col_sums.sort_values(ascending=False).index
df = df[df.columns[:start_col].tolist() + sorted_cols.tolist()]

drop = []
for col in df.columns[start_col:]:
    if (df[col] == 0).all():
        drop.append(col)

df.drop(columns=drop, inplace=True)

# rename columns
for col in df.columns[start_col:-1]:
    if len(col) > 60:
        df.rename(columns={col: col[:55] + "[...]"}, inplace=True)
        

num_colors = len(df.columns[start_col:])
colors = sns.color_palette("hls", num_colors).as_hex()
random.shuffle(colors)
color_dict = {}
for i, component in enumerate(df.columns[start_col:]):
    tuple_component = {component: colors[i]}
    color_dict.update(tuple_component)

color_dict.update(
    {
        "other": "#4c4c4c",
    }
)

# Create the directory for figures if it doesn't exist
fig_dir = "visualisation/individual-methods_supply-chain"
os.makedirs(fig_dir, exist_ok=True)

# workout the max number of lines in the legend
max_lines = 0
for method in methods_full:
    df_method = df[df["method_full"] == method]
    for activity in activities:
        df_activity = df_method[df_method["name"] == activity]
        for scenario in scenarios:
            df_scenario = df_activity[df_activity["db_target"] == scenario].reset_index(
                drop=True
            )
            drop = []
            for col in df_scenario.columns[start_col:]:
                if (df_scenario[col] == 0.0).all():
                    drop.append(col)
            df_scenario.drop(columns=drop, inplace=True)
            col_sums = df_scenario.iloc[:, start_col:].sum()
            sorted_cols = col_sums.sort_values(ascending=False).index
            df_scenario = df_scenario[
                df_scenario.columns[:start_col].tolist() + sorted_cols.tolist()
            ]
            max_lines = max(max_lines, len(df_scenario.columns[start_col:]))

# Plot for each method and scenario

total_figures = len(methods_full) * len(activities) * len(scenarios)
figure_count = 0
pbar = tqdm(total=total_figures, desc="Generating figures")

for method in methods_full:
    df_method = df[df["method_full"] == method]

    for activity in activities:
        df_activity = df_method[df_method["name"] == activity]

        for scenario in scenarios:
            fig, ax = plt.subplots(figsize=fixed_figsize)

            df_scenario = df_activity[df_activity["db_target"] == scenario].reset_index(
                drop=True
            )

            drop = []
            for col in df_scenario.columns[start_col:]:
                if (df_scenario[col] == 0.0).all():
                    drop.append(col)
            df_scenario.drop(columns=drop, inplace=True)

            col_sums = df_scenario.iloc[:, start_col:].sum()
            sorted_cols = col_sums.sort_values(ascending=False).index
            df_scenario = df_scenario[
                df_scenario.columns[:start_col].tolist() + sorted_cols.tolist()
            ]

            # populate the legend elements, and colours
            legend_elements = []
            for i, component in enumerate(df_scenario.columns[start_col:]):
                tuple_component = (component, color_dict[component])
                legend_elements.append(tuple_component)

            # Ensure 'other' is the last element
            sorted_legend_elements = [
                elem for elem in legend_elements if elem[0] != "other"
            ]
            if any(elem[0] == "other" for elem in legend_elements):
                sorted_legend_elements.append(("other", color_dict["other"]))

            # pad legend labels to 60 chars
            for i, elem in enumerate(sorted_legend_elements):
                if len(elem[0]) < 60:
                    sorted_legend_elements[i] = (elem[0].ljust(80), elem[1])
            
            
            legend_lines = [
                Line2D([0], [0], color=color, lw=4, label=label)
                for label, color in sorted_legend_elements
            ]
            
            # add blank lines to the legend to make them the same
            if len(legend_lines) < max_lines:
                for i in range(max_lines - len(legend_lines)):
                    legend_lines.append(Line2D([0], [0], color="white", lw=4, label=""))

            # Create figure for each activity, method, scenario combination

            bar_width = 12  # Increase this value to make bars wider
            years = df_scenario["db_year"].unique()
            for year in years:
                single_bar = df_scenario[df_scenario["db_year"] == year].reset_index(
                    drop=True
                )
                contributions = (
                    single_bar.iloc[:, start_col:]
                    .dropna(axis=1)
                    .drop(columns=["other"])
                    .reset_index(drop=True)
                    .loc[0]
                    .sort_values(ascending=False)
                )

                for c in contributions.index:
                    if contributions[c] == 0.0:
                        contributions.drop(c, inplace=True)

                other = 1 - contributions.sum()
                contributions["other"] = other

                # Assert statement to ensure the total sum is 1.0
                assert (
                    abs(contributions.sum() - 1.0) < 1e-6
                ), f"Contributions do not sum to 1.0: {contributions.sum()}"
                bottom = 0
                for name, contribution in contributions.items():
                    ax.bar(
                        year,
                        contribution,
                        bottom=bottom,
                        color=color_dict[name],
                        label=name,
                        width=bar_width,
                        edgecolor="black",
                        linewidth=0.1,
                    )
                    bottom += contribution

            # Modify x-axis scale or range as needed
            # For example, if years are evenly spaced, you can adjust the xlim to reduce gaps
            ax.set_xlim(
                [min(df_scenario["db_year"]) - 10, max(df_scenario["db_year"]) + 10]
            )
            ax.set_ylim([0, 1.0])

            ax.set_xticks(df_scenario["db_year"].unique(), minor=False)
            ax.set_xticklabels(df_scenario["db_year"].unique())

            # Plotting setup (title, labels, legend, etc.)
            title_raw = f"Contribution by sector for Li-ion battery `{activity}'"
            method_text = f"Pathway of SSP2 scenario (RCP): {scenario}\nLCIA Method: ({method[0]}, {method[2]})"
            ax.text(
                0.01,
                1.02,  # x, y coordinates in axes fraction
                method_text,  # text to display
                horizontalalignment="left",
                fontsize=5,
                fontweight="normal",
                transform=ax.transAxes,
            )

            title = replace_strings_in_string(title_raw, term_replacements)
            ax.set_title(title, fontsize=6, y=1.05, ha='left', x=0.01, fontweight="bold")
            ax.set_ylabel("Normalised score", fontsize=5)
            ax.set_xlabel("Year", fontsize=6)
            ax.tick_params(axis="x", which="both", length=0)

            ax.xaxis.set_tick_params(labelsize=4)
            ax.yaxis.set_tick_params(labelsize=4)

            # Create the legend
            legend = ax.legend(
                handles=legend_lines,
                loc="upper left",
                bbox_to_anchor=(
                    0.0,
                    -0.07,
                ),  # Adjust the vertical position of the legend
                fontsize=4,
                title="Legend: CPC Classification",
                ncol=1,
                frameon=False,
                title_fontsize=5,
                borderpad=2,
                handletextpad=1,
                handlelength=0.5,
            )

            # Save the figure
            filename = f"{method[0]}_{method[1]}_{method[2]}_{scenario}_{activity}.svg"
            filename = filename.replace(" ", "").replace("/", "_")
            filepath = os.path.join(fig_dir, filename)
            
            # adjust the figure size
            plt.gcf().set_size_inches(fixed_figsize[0], fixed_figsize[1])

            # Get current axes position in figure fraction
            current_axes_position = plt.gca().get_position()

            # Adjust bottom margin if needed
            canvas_width, canvas_height = plt.gcf().get_size_inches()
            if canvas_height < fixed_figsize[1]:
                diff = (fixed_figsize[1] - canvas_height) / fixed_figsize[1]
                new_bottom_position = current_axes_position.y0 - diff
                plt.gca().set_position([current_axes_position.x0, new_bottom_position,
                                        current_axes_position.width, current_axes_position.height])

            plt.savefig(filepath, format="svg", bbox_inches='tight')
            plt.close(fig)
            pbar.update(1)

pbar.close()
print("All plots have been generated and saved.")
print(f"Saved to: {fig_dir}")
