import matplotlib.pyplot as plt
import pandas as pd
import os
import matplotlib as mpl
from matplotlib.lines import Line2D
import matplotlib.ticker as mticker
import scienceplots
from tqdm import tqdm
import seaborn as sns
import random
import numpy as np

from utils import replace_string_in_df, term_replacements, replace_strings_in_string
from _00_main import DIR_VISUALISATION, FILE_RESULTS_PROCESSED_TOP_PROCESSES

print("Generating figures for top processes...")


# Create a custom formatter
class CustomFormatter(mticker.ScalarFormatter):
    def __init__(self, fmt="%1.1f"):
        super().__init__(useOffset=False, useMathText=True)
        self.fmt = fmt

    def _set_format(self):
        self.format = self.fmt


# Set a fixed figure size to match your largest plot (274x343 pixels)
# fixed_figsize = (250 / 100, 500 / 100)  # Convert pixels to inches

# plt.rcParams["figure.figsize"] = fixed_figsize
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


# Read in the data
df_raw = pd.read_csv(FILE_RESULTS_PROCESSED_TOP_PROCESSES, sep=";", index_col=None)

for term, replacement in term_replacements.items():
    df_raw = replace_string_in_df(df_raw, term_replacements)

# Aggregate the methods into a single column
method_full = list(zip(df_raw["method_0"], df_raw["method_1"], df_raw["method_2"]))
df_raw.insert(0, "method_full", method_full)


activities = df_raw["name"].unique()
methods_full = df_raw["method_full"].unique()
scenarios = df_raw["db_target"].unique()

df = df_raw.copy().reset_index(drop=True)
# filter out unnecessary columns

cols_tp = [x for x in df.columns if "tp_" in x]
cols_tp_score = [x for x in cols_tp if "score" in x]
cols_tp_name = [x for x in cols_tp if "name" in x]


# Create the directory for figures if it doesn't exist
fig_dir = DIR_VISUALISATION / "individual-methods_top-processes"
os.makedirs(fig_dir, exist_ok=True)

# workout the max number of lines in the legend
max_lines = 0
for method in methods_full:
    df_method = df[df["method_full"] == method]
    for activity in activities:
        df_activity = df_method[df_method["name"] == activity]
        for scenario in scenarios:
            df_scenario = df_activity[df_activity["db_target"] == scenario]
            unique_names = set(
                name
                for name_list in df_scenario[cols_tp_name].values
                for name in name_list
            )
            max_lines = max(max_lines, len(unique_names))

print("Maximum number of unique names in any set:", max_lines)

# After creating your axes (ax), modify the y-axis formatter
formatter = mticker.ScalarFormatter(
    useMathText=True
)  # useMathText for LaTeX styled exponents
plt.gca().yaxis.set_major_formatter(formatter)

# This line sets the size of the offset text (the exponent)
plt.gcf().get_axes()[0].yaxis.get_offset_text().set_fontsize(3)

# To move the offset text (the exponent) to the left of the y-axis
plt.gcf().get_axes()[0].yaxis.get_offset_text().set_verticalalignment("bottom")
plt.gcf().get_axes()[0].yaxis.get_offset_text().set_horizontalalignment("left")
# Define the colour set, given the length of the max number of lines

colors = sns.color_palette("deep", max_lines)

# Plot for each method and scenario

total_figures = len(methods_full) * len(activities) * len(scenarios)
figure_count = 0
pbar = tqdm(total=total_figures, desc="Generating figures")

for method in methods_full:
    df_method = df[df["method_full"] == method]
    for activity in activities:
        df_activity = df_method[df_method["name"] == activity]
        for scenario in scenarios:
            df_scenario = df_activity[df_activity["db_target"] == scenario].reset_index(
                drop=True
            )

            # Create figure for each activity, method, scenario combination
            fig, ax = plt.subplots()  # (figsize=fixed_figsize)
            years = df_scenario["db_year"].unique()

            for year in years:
                single_year_data = df_scenario[df_scenario["db_year"] == year]

                # Plot the total score as a marker
                total_score = single_year_data["score"].iloc[0]
                ax.plot(
                    year,
                    total_score,
                    "x",
                    color="black",
                    markersize=3,
                    label="Total LCIA score",
                )

                bar_width = 4
                # Stacked bar for each top process score
                bottom = 0
                for i in range(1, 6):  # Assuming 5 top processes
                    tp_score = single_year_data[f"tp_{i}_score"].iloc[0]
                    tp_name = single_year_data[f"tp_{i}_name"].iloc[0]
                    ax.bar(
                        year,
                        tp_score,
                        bottom=bottom,
                        label=tp_name,
                        color=colors[i - 1],
                        width=bar_width,
                        edgecolor="black",
                        linewidth=0.5,
                    )
                    bottom += tp_score

                # Use plain style for y-ticks (no scientific notation)
            ax.ticklabel_format(style="plain", axis="y")

            # Get the exponent for the scientific notation manually
            ticks = ax.get_yticks()
            if ticks[-1] != 0:
                exponent = np.sign(ticks[-1]) * np.fix(
                    np.abs(np.log10(np.abs(ticks[-1])))
                ).astype(int)
            else:
                exponent = 0
            # ax.set_yticklabels([])

            # Set the offset text - manually place it
            if exponent != 0:
                ax.text(
                    -0.05,
                    1.0,
                    r"$(\times10^{" + str(exponent) + "})$",
                    va="top",
                    transform=ax.transAxes,
                    fontsize=4,
                )

            # Modify x-axis scale or range as needed
            ax.set_xlim(
                [min(df_scenario["db_year"]) - 5, max(df_scenario["db_year"]) + 5]
            )

            # Set x-ticks at every position where you have data
            ax.set_xticks(years)

            # Set labels with a label every 10 years, empty string otherwise
            labels = [str(year) if year % 10 == 0 else "" for year in years]
            ax.set_xticklabels(labels)

            # Plotting setup (title, labels, legend, etc.)
            title_raw = f"Total LCIA score and top five processes for Li-ion battery: `{activity}'"
            method_text = f"Pathway of SSP2 scenario (RCP): {scenario}\nLCA Method: ({method[0]}, {method[2]})"
            ax.text(
                0.01,
                1.02,  # x, y coordinates in axes fraction
                method_text,  # text to display
                horizontalalignment="left",
                fontsize=5,
                fontweight="normal",
                transform=ax.transAxes,
            )
            unit = df_scenario["unit"].iloc[0]
            title = replace_strings_in_string(title_raw, term_replacements)
            ax.set_title(
                title, fontsize=7, y=1.06, ha="left", x=0.01, fontweight="bold"
            )
            ax.set_ylabel(f"LCIA score: {unit} / kg (battery)", fontsize=7)
            ax.set_xlabel(f"Scenario year in SSP2 (RCP: {scenario})", fontsize=7)
            ax.tick_params(axis="x", which="major", length=2)
            ax.tick_params(axis="x", which="minor", length=0)
            ax.xaxis.set_tick_params(labelsize=6)
            ax.yaxis.set_tick_params(labelsize=6)

            unique_names = set()
            for i in range(1, 6):  # Assuming 5 top processes
                unique_names.update(df_scenario[f"tp_{i}_name"].unique())

            # trim the names to 60 characters, add ellipsis if needed after 60 characters
            unique_names = [
                name[:60] + (name[60:] and "[...]") for name in unique_names
            ]

            legend_handles = [
                Line2D([0], [0], color=colors[i], label=name)
                for i, name in enumerate(unique_names)
            ]

            # Create the legend with these handles
            ax.legend(
                handles=legend_handles,
                loc="upper left",
                bbox_to_anchor=(0.0, -0.06),
                fontsize=5,
                title="Legend: Top five processes",
                ncol=1,
                frameon=False,
                title_fontsize=6,
                borderpad=5,
                handletextpad=1,
                handlelength=0.5,
            )

            # Save the figure
            filename = f"{method[0]}_{method[1]}_{method[2]}_{scenario}_{activity}_top-processes.svg"
            filename = filename.replace(" ", "").replace("/", "_")
            filepath = os.path.join(fig_dir, filename)

            # adjust the figure size
            # plt.gcf().set_size_inches(fixed_figsize[0], fixed_figsize[1])

            # Get current axes position in figure fraction
            # current_axes_position = plt.gca().get_position()

            # # Adjust bottom margin if needed
            # canvas_width, canvas_height = plt.gcf().get_size_inches()
            # if canvas_height < fixed_figsize[1]:
            #     diff = (fixed_figsize[1] - canvas_height) / fixed_figsize[1]
            #     new_bottom_position = current_axes_position.y0 - diff
            #     plt.gca().set_position(
            #         [
            #             current_axes_position.x0,
            #             new_bottom_position,
            #             current_axes_position.width,
            #             current_axes_position.height,
            #         ]
            #     )

            plt.savefig(filepath, format="svg", bbox_inches="tight")
            plt.close(fig)
            pbar.update(1)

pbar.close()
print("All plots have been generated and saved.")
print(f"Saved to: {fig_dir}")
