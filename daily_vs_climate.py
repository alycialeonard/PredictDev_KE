#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Filename: daily_vs_climate_old.py
Author: Alycia Leonard
Date: 2026-06-24
Version: 1.0
Description: Analysis for daily infrastructure priorities vs climate infrastructure priorities
License: GNU GPL-3.0
Contact: alycia.leonard@eng.ox.ac.uk
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import numpy as np

# Define paths
cwd = os.getcwd()
survey_path = os.path.join(cwd, "data", "Kenya_UPV_Survey_Preprocessed_AllCols.csv")
utterances_path = os.path.join(cwd, "data", "Kenya_UPV_Utterances.csv")
results_path = os.path.join("results", 'daily_vs_climate')

# Helper for ranked-choice parsing
def split_choices(value):
    # Return no items when the survey cell is missing
    if pd.isna(value):
        return []
    # Convert the cell to clean text
    text = str(value).strip()
    # Remove square brackets and quote marks if a cell looks like a printed Python list
    text = text.replace("[", "").replace("]", "").replace("'", "").replace('"', "")
    # Split the text at commas and remove blank fragments
    choices = [item.strip() for item in text.split(",") if item.strip()]
    # Return the ordered item list
    return choices

# Make dictionary assigning item to infrastructure types
item_types = {
    "Water": ["Borehole", "Rainwater Harvesting System", "River", "Overhead Water Tank", "Water", "Watering Can",
              "Jerrycan", "Water Pump", "Irrigation", "Irrigation Pump", "Shower"],
    "Electricity": ["Solar PV System", "Electricity", "Battery", "Generator", "Grain Mill", "Grinder", "Light Bulb",
                    "Torch", "Fridge", "Fan", "Electric Iron", "Electric Pressure Cooker", "TV", "Kerosene Lantern",
                    "Fire", "Charcoal Stove", "Gas Stove", "Wood Stove", "Stove"],
    "Transport": ["Motorcycle", "Boat", "Car", "Bike", "Donkey and Cart", "Road"],
    "Health": ["Doctor", "Hospital", "Medicine"],
    "Sanitation": ["Toilet Squat", "Toilet Flush", "Disposable Sanitary Pad"],
    "Shelter": ["House", "Corrugated Iron Sheet", "Furniture"],
    "Communication": ["Mobile Phone", "Computer", "Radio"],
    "Education": ["School"],
}

# Make reverse dictionary for easier lookup of types based on items
item_to_type = {item: category for category, items in item_types.items() for item in items}

# Make list of types
infra_types = list(item_types.keys()).append("Other")

# Define shorthand for frequently-used columns
daily_col = "Which 5 items are most important to you in your daily life? Please indicate these in order of importance, starting with the most important"
shock_items_col = "Given the chosen climate event - which 3 items are most useful to you?"
shock_col = "What extreme climate event are you most worried about?"

# ------------- Get dataframe of priorities by respondent --------------

# Load survey data
survey_df = pd.read_csv(survey_path, low_memory=False)

# Empty list for the loop below
priorities_list = []

# Get priority items and types in each context for each respondent in a table
for context_name, item_column in [("Daily", daily_col), ("Shock", shock_items_col)]:
    # For each respondent
    for row_number, respondent in survey_df.iterrows():
        # Convert the respondent's comma-separated ranked choices into an ordered list
        selected_items = split_choices(respondent[item_column])
        # For each item selected in rank order
        for rank_number, item_name in enumerate(selected_items, start=1):
            # Add a row for this respondent, context, rank, and item.
            priorities_list.append({
                "Interview ID": respondent["Interview ID"],
                "context": context_name,
                "rank": rank_number,
                "item": item_name,
                "infra_type": item_to_type.get(item_name, "Other"),
                "shock": respondent[shock_col] if context_name == "Shock" else pd.NA
            })

# Convert the priority list into a dataframe and save.
priorities_df = pd.DataFrame(priorities_list)
priorities_df.to_csv(os.path.join(results_path, 'priorities.csv'), index=False)

# Collect the names of items that were not assigned a type and save in case needed for review.
unmapped_items = sorted(priorities_df.loc[priorities_df["infra_type"] == "Other", "item"].unique())
pd.DataFrame({"unmapped_item": unmapped_items}).to_csv(os.path.join(results_path, "unmapped_items.csv"), index=False)

# ------------- Infrastructure priorities by context (daily vs shock)  --------------

# Throw out the daily priorities 4 and 5 (so same number of choices are made for each)
priorities_df = priorities_df[priorities_df["rank"] <= 3]

# Drop all the "Other" rows
priorities_df = priorities_df[priorities_df["infra_type"] != "Other"]

# Get count and weight (by rank) for every unique combination of context + infrastructure type (NOT shock specific)
grouped_df = priorities_df.groupby(["context"] + ["infra_type"], dropna=False, observed=False).agg(counts=("rank", "size"), weight=("rank", "sum")).reset_index()

# Get as a percentage of total responses in that context
grouped_df["counts_normalised"] = grouped_df["counts"] / grouped_df.groupby("context")["counts"].transform("sum")
grouped_df["percentage"] = grouped_df["counts_normalised"] * 100
grouped_df.to_csv(os.path.join(results_path, "priorities_grouped.csv"), index=False)

# Plot in grouped bar chart, sorted by daily order
plot_df = grouped_df.pivot(index="infra_type", columns="context", values="percentage").fillna(0)
plot_df = plot_df.sort_values(by="Daily", ascending=False)
ax = plot_df.plot(kind="bar", figsize=(10, 5), colormap="tab10")
plt.ylabel("% of selections for that context")
ax.set_xlabel("Infrastructure Type")
ax.yaxis.set_major_locator(MultipleLocator(10))
ax.yaxis.set_minor_locator(MultipleLocator(2))
ax.grid(axis="y", which="major", linewidth=0.8, alpha=0.6)
ax.grid(axis="y", which="minor", linewidth=0.5, alpha=0.3)
ax.set_axisbelow(True)
ax.legend(title="Context", framealpha=1)
plt.tight_layout()
plt.savefig(os.path.join(results_path, "daily_vs_shock.png"), dpi=200)
plt.close()

# --------------- Infrastructure priorities by shock ------------------------------

# Ditch the daily life rows, keep shocks only
shock_priorities_df = priorities_df[priorities_df["context"] == "Shock"]

# Get count and weight (by rank) for every unique combination of infrastructure type + shock
grouped_by_shock_df = (shock_priorities_df.groupby(["infra_type"] + ["shock"], dropna=False, observed=False).agg(counts=("rank", "size"), weight=("rank", "sum")).reset_index())

# Get as a percentage of total responses in that shock group
grouped_by_shock_df["counts_normalised"] = grouped_by_shock_df["counts"] / grouped_by_shock_df.groupby("shock")["counts"].transform("sum")
grouped_by_shock_df["percentage"] = grouped_by_shock_df["counts_normalised"] * 100
grouped_by_shock_df.to_csv(os.path.join(results_path, "priorities_grouped_by_shock.csv"), index=False)

# Define plot order based on relative selection rate for daily case
order = ["Water", "Transport", "Shelter", "Electricity", "Communication", "Health", "Education", "Sanitation"]

# Plot in grouped bar chart. Drop hurricane as a shock because it's only picked three times so it looks wild
grouped_by_shock_df = grouped_by_shock_df[grouped_by_shock_df["shock"] != "Hurricane"]
grouped_by_shock_df.dropna(subset=["shock"], inplace=True)
plot_df = grouped_by_shock_df.pivot(index="infra_type", columns="shock", values="percentage").fillna(0)
plot_df = plot_df.reindex(order).dropna(how="all")
ax = plot_df.plot(kind="bar", figsize=(10, 5), colormap="tab10")
ax.set_xlabel("Infrastructure Type")
ax.yaxis.set_major_locator(MultipleLocator(10))
ax.yaxis.set_minor_locator(MultipleLocator(2))
ax.grid(axis="y", which="major", linewidth=0.8, alpha=0.6)
ax.grid(axis="y", which="minor", linewidth=0.5, alpha=0.3)
ax.set_axisbelow(True)
ax.legend(title="Shock", framealpha=1)
plt.ylabel("% of selections for that shock")
plt.tight_layout()
plt.savefig(os.path.join(results_path, "by_shock_type.png"), dpi=200)
plt.close()

# ---------------- Tornado plot: shock priorities relative to daily priorities ----------------

# Daily and per-shock percentages for each infrastructure type
daily_rates = grouped_df[grouped_df["context"] == "Daily"].set_index("infra_type")["percentage"]
shock_rates = grouped_by_shock_df.pivot(index="infra_type",columns="shock",values="percentage").fillna(0)

# Calculate difference from each shock to daily-life priorities
difference_df = shock_rates.sub(daily_rates, axis=0)

# Sort diff file with infrastructure types by their daily selection percentage, save
tornado_order = daily_rates.sort_values(ascending=True).index
difference_df = difference_df.reindex(tornado_order)
daily_rates = daily_rates.reindex(tornado_order)
difference_df.to_csv(os.path.join(results_path, "shock_difference_from_daily.csv"))

# Plot the differences
ax = difference_df.plot(kind="barh",figsize=(10, 12),colormap="tab10",width=0.6)
# Central reference line: no difference from daily-life percentage
ax.axvline(0, linewidth=1.2)
ax.set_xlabel("Difference from daily-life selection (%)")
ax.set_ylabel("Infrastructure Type# ")
ax.xaxis.set_major_locator(MultipleLocator(10))
ax.xaxis.set_minor_locator(MultipleLocator(1))
ax.grid(axis="x",which="major",linewidth=0.8,alpha=0.6)
ax.grid(axis="x",which="minor",linewidth=0.5,alpha=0.3)
ax.set_axisbelow(True)
ax.legend(title="Shock",framealpha=1,loc="upper left")
ax.set_xlim(-40, 40)
# Label bars with numeric diffs
for bar in ax.patches:
    x = bar.get_width()
    y = bar.get_y() + bar.get_height() / 2
    if x >= 0:
        ax.text(x + 0.5, y, f"{x:+.1f}", va="center", ha="left", fontsize=8)
    else:
        ax.text(x - 0.5, y, f"{x:+.1f}", va="center", ha="right", fontsize=8)
plt.tight_layout()
plt.savefig(os.path.join(results_path, "shock_difference_from_daily.png"),dpi=200)
plt.close()

# --------------- Infrastructure priorities by demographic for drought ------------------------------

# Define one-hot indicators to treat as demographic subgroups
subgroups = [
    # Age
    "Age (Range)_18 - 25",
    "Age (Range)_25 - 30",
    "Age (Range)_30 - 35",
    "Age (Range)_35 - 40",
    "Age (Range)_40 - 45",
    "Age (Range)_45 - 50",
    "Age (Range)_55 - 60",
    "Age (Range)_60 - 65",
    "Age (Range)_65 - 70",
    "Age (Range)_75 - 80",
    # Gender
    "What is your gender?_Female",
    "What is your gender?_Male",
    # County
    "County Name_Machakos (Kenya)",
    "County Name_Narok (Kenya)",
    "County Name_Turkana (Kenya)",
    # TODO Add income
    # Education
    "What is the highest level of education you have completed?_Bachelors or Masters",
    "What is the highest level of education you have completed?_No formal education",
    "What is the highest level of education you have completed?_Other",
    "What is the highest level of education you have completed?_PhD or more",
    "What is the highest level of education you have completed?_Primary",
    "What is the highest level of education you have completed?_Secondary (high school)",
    "What is the highest level of education you have completed?_Technical training",
    # Disability
    "Do you have a disability?_No",
    "Do you have a disability?_Yes",
    # Occupation
    "What is your main occupation?_Accountant",
    "What is your main occupation?_Farmer-animals",
    "What is your main occupation?_Farmer-crops",
    "What is your main occupation?_Fisherman",
    "What is your main occupation?_Government jobholder",
    "What is your main occupation?_Housework unpaid",
    "What is your main occupation?_IT sector",
    "What is your main occupation?_Other",
    "What is your main occupation?_Private jobholder",
    "What is your main occupation?_Retired",
    "What is your main occupation?_Small business employee",
    "What is your main occupation?_Small business owner",
    "What is your main occupation?_Student",
    "What is your main occupation?_Teacher",
    "What is your main occupation?_Unemployed"
]

# Isolate only respondents who selected drought in priorities.
drought_interview_ids = priorities_df.loc[priorities_df["shock"] == "Drought", "Interview ID"]
drought_priorities_df = priorities_df[priorities_df["Interview ID"].isin(drought_interview_ids)].copy()

# Store grouped results for all demographic subgroups
demographic_results = []

# For each subgroup, get daily vs drought priorities and plot
for target in subgroups:

    # Get subgroup priorities
    target_priorities_df = drought_priorities_df [drought_priorities_df["Interview ID"].isin(survey_df.loc[survey_df[target] == 1, "Interview ID"])].copy()
    # Group by context (since all Shock rows are now Drought rows)
    target_grouped_df = target_priorities_df.groupby(["context"] + ["infra_type"], dropna=False, observed=False).agg(counts=("rank", "size"), weight=("rank", "sum")).reset_index()
    # Get as a percentage of total responses in that context
    target_grouped_df["counts_normalised"] = target_grouped_df["counts"] / target_grouped_df.groupby("context")["counts"].transform("sum")
    target_grouped_df["percentage"] = target_grouped_df["counts_normalised"] * 100

    # Label results by group and store in demographic_results
    target_grouped_df["group"] = target
    demographic_results.append(target_grouped_df)

    # Plot in grouped bar chart, sorted by daily order
    plot_df = target_grouped_df.pivot(index="infra_type", columns="context", values="percentage").fillna(0)
    # plot_df = plot_df.sort_values(by="Daily", ascending=False)
    plot_df = plot_df.reindex(order).dropna(how="all")
    ax = plot_df.plot(kind="bar", figsize=(10, 5), colormap="tab10")
    plt.ylabel("% of selections for that context")
    plt.title(f"{target}")
    ax.set_xlabel("Infrastructure Type")
    ax.yaxis.set_major_locator(MultipleLocator(10))
    ax.yaxis.set_minor_locator(MultipleLocator(2))
    ax.grid(axis="y", which="major", linewidth=0.8, alpha=0.6)
    ax.grid(axis="y", which="minor", linewidth=0.5, alpha=0.3)
    ax.set_axisbelow(True)
    ax.legend(title="Context", framealpha=1)
    plt.tight_layout()
    plt.savefig(os.path.join(results_path, f"daily_vs_shock_{target}.png"), dpi=200)
    plt.close()

# Get df from store of results, save to csv
demographic_df = pd.concat(demographic_results, ignore_index=True)
demographic_df.to_csv(os.path.join(results_path, 'demographic_priorities.csv'), index=False)


# Put each group's percentages in separate columns
diff_df = demographic_df.pivot(index=["infra_type", "context"], columns="group", values="percentage").fillna(0)

# Get diff between paired demographics
diff_df["Women minus Men"] = diff_df["What is your gender?_Female"] - diff_df["What is your gender?_Male"]
# Put Daily and Shock differences in separate columns
plot_df = diff_df["Women minus Men"].unstack("context")

# Plot differences
plot_df = plot_df.reindex(order).dropna(how="all")
ax = plot_df.plot(kind="bar",figsize=(10, 5),colormap="tab10")
ax.axhline(0, linewidth=1.2)
ax.set_ylabel("Women minus men selection rate (percentage points)")
ax.set_xlabel("Infrastructure Type")
ax.set_title("Gender difference in daily and drought priorities")
ax.yaxis.set_major_locator(MultipleLocator(5))
ax.yaxis.set_minor_locator(MultipleLocator(1))
ax.grid(axis="y", which="major", linewidth=0.8, alpha=0.6)
ax.grid(axis="y", which="minor", linewidth=0.5, alpha=0.3)
ax.set_axisbelow(True)
ax.legend(title="Context", framealpha=1)
plt.tight_layout()
plt.savefig(os.path.join(results_path, "gender_difference_daily_vs_drought.png"),dpi=200)
plt.close()