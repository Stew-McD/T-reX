import matplotlib as mpl
from matplotlib.lines import Line2D
import scienceplots
import pandas as pd
import numpy as np
import os

from utils import *


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

title = "Li-ion batteries:"
mpl.style.use(["science", "scatter"])
mpl.rcParams.update(rc_fonts)

import matplotlib.pyplot as plt

from _00_main import FILE_RESULTS_PROCESSED, DIR_VISUALISATION
from utils import term_replacements, replace_strings_in_string

# # for testing
# x = np.linspace(0, 10, 100)
# y = np.sin(x)
# plt.plot(x, y)

# make sure of the correct working directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

FILE_IN = FILE_RESULTS_PROCESSED

# read in the data
df_raw = pd.read_csv(FILE_IN, sep=";", index_col=None)

df_raw.sort_values(
    by=["method_0", "method_1", "method_2", "db_target", "db_year"], inplace=True
)

df_raw["method_full"] = list(
    zip(df_raw["method_0"], df_raw["method_1"], df_raw["method_2"])
)

total_methods = len(df_raw.method_full.unique())

activities = df_raw.name.unique()  # eg. ["NMC111", "NCA", "NMC811", "LFP", "LiMn2O4"]
scenarios = df_raw.db_target.unique()  # eg. ["Base", "PkBudg500"]
years = df_raw.db_year.unique()  # eg. [2020, 2030, 2040, 2050]
methods_0 = df_raw.method_0.unique()
methods_1 = df_raw.method_1.unique()
methods_2 = df_raw.method_2.unique()
width_1 = 90  # mm
width_3on2 = 140  # mm
width_2 = 190  # mm

markers = ["o", "x", "^", "D", "*", "s"]  # Add more markers as needed
marker_weight = 1

colorblind_friendly_palette = [
    "#377eb8",
    "#ff7f00",
    "#4daf4a",
    "#e41a1c",
    "#984ea3",
    "#a65628",
    "#999999",
    "#dede00",
    "#f781bf",
]


colors = colorblind_friendly_palette

loosely_dotted = (0, (1, 3))
loosely_dashed = (0, (3, 5))
line_styles = [
    loosely_dotted,
    loosely_dashed,
    "-.",
    "-",
]  # Add more line styles as needed
line_width = 0.25  # Line width

# Create a directory for the saved plots if it doesn't already exist
os.makedirs(DIR_VISUALISATION / "individual-methods", exist_ok=True)

# Generate and save plots for each method in method_sets
print(
    f"Generating individual plots for {len(methods_0)} method sets: total {total_methods} plots"
)
counter = 0
for a, method_0 in enumerate(methods_0):
    df_methods_0 = df_raw[df_raw["method_0"] == method_0]

    for b, method_1 in enumerate(methods_1):
        df_methods_1 = df_methods_0[df_methods_0["method_1"] == method_1]

        for c, method_2 in enumerate(methods_2):
            df_methods_2 = df_methods_1[df_methods_1["method_2"] == method_2]

            if df_methods_2.empty:
                continue

            fig, ax = plt.subplots()
            title_raw = f"LCIA score with method: {df_methods_2['method_0'].iloc[0]}\n{method_1}, {method_2}"

            title = replace_strings_in_string(title_raw, term_replacements)

            # if len(title) > 50:
            #     print(f'TITLE RAW: \n\t{title_raw}')
            #     print(f'TITLE: \n\t{title}')

            plt.title(title, fontsize=8.5)
            ax.set_xlabel("Year", fontsize=8)
            ax.set_ylabel(f"{df_methods_2['unit'].iloc[0]} / kg (battery)", fontsize=8)

            # Modify x-axis scale or range as needed
            ax.set_xlim(
                [min(df_methods_2["db_year"]) - 5, max(df_methods_2["db_year"]) + 5]
            )

            # Set x-ticks at every position where you have data
            ax.set_xticks(years)

            # Set labels with a label every 10 years, empty string otherwise
            labels = [str(year) if year % 10 == 0 else "" for year in years]
            ax.set_xticklabels(labels)
            ax.tick_params(axis="x", which="major", length=2)
            ax.tick_params(axis="x", which="minor", length=0)
            ax.yaxis.set_tick_params(labelsize=6)
            ax.xaxis.set_tick_params(labelsize=6)

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

            for d, activity in enumerate(activities):
                for e, scenario in enumerate(scenarios):
                    df_activity_scenario = df_methods_2[
                        (df_methods_2["name"] == activity)
                        & (df_methods_2["db_target"] == scenario)
                    ]
                    ax.plot(
                        df_activity_scenario["db_year"],
                        df_activity_scenario["score"],
                        label=f"{activity} ({scenario})",
                        marker=markers[e % len(markers)],
                        linestyle=line_styles[e % len(line_styles)],
                        linewidth=line_width,
                        fillstyle="none",
                        color=colors[d % len(colors)],
                        markersize=3,
                        markeredgewidth=0.25,
                    )

                    # Create the legends outside the plot area
            legend_elements_activities = [
                Line2D(
                    [0],
                    [0],
                    color=color,
                    lw=2,
                    label=activity,
                    markerfacecolor=color,
                    markeredgecolor=color,
                    marker="s",
                    linestyle="none",
                )
                for activity, color in zip(activities, colors)
            ]

            legend_elements_scenarios = [
                Line2D(
                    [0],
                    [0],
                    marker=marker,
                    color="black",
                    label=scenario,
                    markersize=2,
                    linewidth=line_width,
                    linestyle=linestyle,  # use the linestyle associated with the scenario
                    markeredgewidth=0.3,
                    markerfacecolor="none",
                )
                for scenario, marker, linestyle in zip(scenarios, markers, line_styles)
            ]

            # Add the legends to the plot outside the plot area
            legend_activities = ax.legend(
                handles=legend_elements_activities,
                title="Battery:",
                title_fontsize=7,
                fontsize=5,
                bbox_to_anchor=(1.02, 0.5),
                loc="lower left",
            )
            ax.add_artist(
                legend_activities
            )  # Add the first legend manually to the current Axes.
            legend_scenarios = ax.legend(
                handles=legend_elements_scenarios,
                title="Scenario:\n(SSP2)",
                title_fontsize=7,
                fontsize=5,
                bbox_to_anchor=(1.02, 0.5),
                loc="upper left",
            )

            # Define filename and save plot
            filename = (
                f"{method_0}-{method_1}-{method_2}.svg"  # Changed from .pdf to .svg
            )
            filename_safe = filename.replace(
                "/", "|"
            )  # Replacing any forward slashes to avoid path issues
            filepath = os.path.join(
                DIR_VISUALISATION / "individual-methods", filename_safe
            )
            plt.savefig(filepath, format="svg", bbox_inches="tight")  # Saving as SVG
            # plt.show()
            plt.close(fig)

            # print progress
            counter += 1
            print(
                f"Saved : {counter} of {total_methods}: ({method_0}, {method_1}, {method_2})"
            )
