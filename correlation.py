#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Filename: correlation.py
Author: Alycia Leonard
Date: 2025-12-08
Version: 1.0
Description: understand the correlation between the access and importance for a single item
License: GNU GPL-3.0
Contact: alycia.leonard@eng.ox.ac.uk
"""

import pandas as pd
import os
from sklearn.metrics import matthews_corrcoef

# Load data
cwd = os.getcwd()
data_path = os.path.join(cwd, 'data')
df = pd.read_csv(os.path.join(data_path, 'Kenya_UPV_Survey_Preprocessed_EncodedCols_2.csv'))
pairs = pd.read_csv(os.path.join(data_path, 'correlations.csv'))

# Create a directory for outputs
output_dir = os.path.join(cwd, "results", "correlation")
os.makedirs(output_dir, exist_ok=True)

# For each pair of variables
for index, row in pairs.iterrows():
    # get their names
    var1 = row['var1']
    var2 = row['var2']

    # Extract the series from the dataset
    v1 = df[var1]
    v2 = df[var2]

    # Get Matthews correlation coefficient (better for binary variables)
    mcc = matthews_corrcoef(v1, v2)

    # Get and print all the correlations:
    print("Columns:")
    print(f"- {var1}")
    print(f"- {var2}")
    print("Matthews Correlation Coefficient (MCC):", mcc)

    # Get profiles for positives for each variable & intersection
    group_v1 = df[(v1 == 1)].mean()
    group_v2 = df[(v2 == 1)].mean()
    # group_v1v2 = df[(v1 == 1) & (v2 == 1)].mean()

    # Build one combined DataFrame & save
    combined = pd.DataFrame({f"profile_{var1}": group_v1, f"profile_{var2}": group_v2}) #, f"profile_{var1}_{var2}": group_v1v2})
    combined.to_csv(os.path.join(output_dir, f"profiles_{var1}_{var2}.csv"))


# # Get the correlation between the two
# correlation = access.corr(importance)
# print("Correlation between access and importance:", correlation)
#
# # Get a table of their overlap
# overlap_table = pd.crosstab(access, importance)
# print("\nOverlap between access and importance:\n", overlap_table)
#
# # Characterise the groups by answer
# numeric_cols = df.select_dtypes(include="number").columns
# group_access1_imp1 = df[(access == 1) & (importance == 1)][numeric_cols].mean()
# group_access1_imp0 = df[(access == 1) & (importance == 0)][numeric_cols].mean()
# group_access0_imp1 = df[(access == 0) & (importance == 1)][numeric_cols].mean()
#
# print("\nProfile: Access = 1 and Importance = 1\n", group_access1_imp1)
# print("\nProfile: Access = 1 and Importance = 0\n", group_access1_imp0)
# print("\nProfile: Access = 0 and Importance = 1\n", group_access0_imp1)
#
# # Differences between the two groups
# group_diff = group_access1_imp1 - group_access1_imp0
# print("\nDifferences between access+important group and access+unimportant group:\n", group_diff)
#
# # Create a directory for outputs
# output_dir = os.path.join(cwd, "results", "correlation")
# os.makedirs(output_dir, exist_ok=True)
#
# # Save correlation as a one-row CSV
# pd.DataFrame({"correlation": [correlation]}).to_csv(os.path.join(output_dir, "correlation.csv"), index=False)
#
# # Save matthews correlation as a one-row CSV
# pd.DataFrame({"mcc": [mcc]}).to_csv(os.path.join(output_dir, "mcc.csv"), index=False)
#
# # Save overlap table
# overlap_table.to_csv(os.path.join(output_dir, "overlap_table.csv"))
#
# # Save group profiles
# group_access1_imp1.to_csv(os.path.join(output_dir, "profile_access1_importance1.csv"))
# group_access1_imp0.to_csv(os.path.join(output_dir, "profile_access1_importance0.csv"))
# group_access0_imp1.to_csv(os.path.join(output_dir, "profile_access0_importance1.csv"))
#
# # Save group differences
# group_diff.to_csv(os.path.join(output_dir, "difference_access1groups.csv"))
#
# print("\nAll results saved to:", output_dir)

