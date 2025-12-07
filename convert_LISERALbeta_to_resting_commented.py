###################################################################################################
######### Define functions to convert liseral output to csv in R GIMME output format ##############
# This function converts the beta output files (in the same directory) extracted from LISERAL into 
# a csv format that is compatible with the R GIMME package output format for further analysis.
# This script is for converting regular GIMME outputs, not for indSEM outputs. Specifically, the 
# difference is in how group-level and individual-level paths are defined.
# The converted output csv file will contain columns:
# 'file' (original complex filename), 'ff_id' (extracted five-digit participant ID), 
# 'lhs', 'rhs', 'beta', 'level' (group or ind)
# Note, the way ff_id is extracted assumes the original complex filename contains 'csm14aff' 
# followed by the five-digit ID.
####################################################################################################

import pandas as pd
import os
import sys

####################################### EDIT AS NEEDED ###################################################
# Mapping of VAR codes to descriptive names of the ROIs - should match those used in R GIMME

MAPPING = {
    'VAR1': 'DMN_1lag', 'VAR2': 'DMN_2lag', 'VAR3': 'DMN_3lag', 'VAR4': 'DMN_4lag', 'VAR5': 'DMN_5lag', 'VAR6': 'DMN_6lag',
    'VAR7': 'SAL_1lag', 'VAR8': 'SAL_2lag', 'VAR9': 'SAL_3lag', 'VAR10': 'SAL_4lag', 'VAR11': 'SAL_5lag', 'VAR12': 'SAL_6lag',
    'VAR13': 'FPN_1lag', 'VAR14': 'FPN_2lag', 'VAR15': 'FPN_3lag', 'VAR16': 'FPN_4lag', 'VAR17': 'FPN_5lag', 'VAR18': 'FPN_6lag',
    'VAR19': 'DMN_1', 'VAR20': 'DMN_2', 'VAR21': 'DMN_3', 'VAR22': 'DMN_4', 'VAR23': 'DMN_5', 'VAR24': 'DMN_6',
    'VAR25': 'SAL_1', 'VAR26': 'SAL_2', 'VAR27': 'SAL_3', 'VAR28': 'SAL_4', 'VAR29': 'SAL_5', 'VAR30': 'SAL_6',
    'VAR31': 'FPN_1', 'VAR32': 'FPN_2', 'VAR33': 'FPN_3', 'VAR34': 'FPN_4', 'VAR35': 'FPN_5', 'VAR36': 'FPN_6'
}
##########################################################################################################

####################################### EDIT AS NEEDED ###################################################
# Specify output filename
OUTPUT_FILENAME = "GIMME_r_format_output.csv"
##########################################################################################################

def process_beta_file(beta_path: str, file_id: str, group_pairs: set) -> pd.DataFrame:
    """
    Process a single beta CSV, return a DataFrame with columns [file, lhs, rhs, beta, level].
    """
    df = pd.read_csv(beta_path, index_col=0)
    df.index.name = 'lhs'

    long_df = (
        df.reset_index()
          .melt(id_vars='lhs', var_name='rhs', value_name='beta')
          .query('beta != 0')
    )

    # Clean and map VAR codes
    for col in ['lhs', 'rhs']:
        long_df[col] = (
            long_df[col].astype(str)
                      .str.replace(r'\s+', '', regex=True)
                      .map(MAPPING)
        )

    long_df['file'] = file_id
    # Assign level based on reference group pairs
    long_df['level'] = long_df.apply(
        lambda row: 'group' if (row['lhs'], row['rhs']) in group_pairs else 'ind',
        axis=1
    )

    return long_df[['file', 'lhs', 'rhs', 'beta', 'level']]


def main(root_dir: str, reference_path: str) -> None:
    # Load reference file
    ref_df = pd.read_csv(reference_path)

    # Extract participant ID (five digits after 'csm14aff')
    ref_df['id'] = ref_df['file'].astype(str).str.extract(r'csm14aff(\d{5})')

    # Prepare group-level pairs from reference
    ref_df['lhs'] = ref_df['lhs'].astype(str).str.strip()
    ref_df['rhs'] = ref_df['rhs'].astype(str).str.strip()
    group_pairs = set(
        tuple(x) for x in ref_df.loc[ref_df['level'] == 'group', ['lhs', 'rhs']].values
    )

    # Map each ID to its original complex file name
    id_to_complex = {
        id_val: ref_df.loc[ref_df['id'] == id_val, 'file'].iloc[0]
        for id_val in ref_df['id'].dropna().unique()
    }

    processed_ids = set()
    all_dfs = []

    # Iterate through participant subdirectories
    for entry in os.listdir(root_dir):
        subdir = os.path.join(root_dir, entry)
        if os.path.isdir(subdir):
            beta_file = f"{entry}_beta.csv"
            beta_path = os.path.join(subdir, beta_file)
            if os.path.isfile(beta_path):
                processed_ids.add(entry)
                df_out = process_beta_file(beta_path, entry, group_pairs)
                all_dfs.append(df_out)
            else:
                print(f"Warning: missing beta file for {entry}: {beta_path}")

    if not all_dfs:
        print("No beta files processed. Exiting.")
        return

    # Compile beta outputs
    beta_df = pd.concat(all_dfs, ignore_index=True)
    beta_df['file'] = beta_df['file'].astype(int)
    # Replace with original complex filenames
    beta_df['file'] = beta_df['file'].astype(str).map(id_to_complex)

    # Keep reference rows for IDs not processed
    ref_keep = ref_df.loc[~ref_df['id'].isin(processed_ids), ['file', 'lhs', 'rhs', 'beta', 'level']].copy()

    # Combine
    combined_df = pd.concat([ref_keep, beta_df], ignore_index=True)

    # Extract numeric ID for sorting and as ff_id
    combined_df['ff_id'] = combined_df['file'].astype(str).str.extract(r'csm14aff(\d{5})')
    combined_df['ff_id'] = combined_df['ff_id'].astype(int)

    # Define 'level' for proper ordering
    combined_df['level'] = pd.Categorical(combined_df['level'], categories=['group', 'ind'], ordered=True)

    # Sort by ff_id then level
    combined_df = combined_df.sort_values(by=['ff_id', 'level'])

    # Reorder columns: file, ff_id, lhs, rhs, beta, level
    combined_df = combined_df[['file', 'ff_id', 'lhs', 'rhs', 'beta', 'level']]

    # Write final output
    combined_df.to_csv(OUTPUT_FILENAME, index=False)
    print(f"Saved combined and replaced output to {OUTPUT_FILENAME}")


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <root_folder> <reference_csv>")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2])
