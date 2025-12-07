###################################################################################################
######### Function to search through R-based GIMME output folder for beta & psi anomalies #########
# This function searches through an indSEM GIMME output folder structure for beta and psi files
# that contain any values greater than 1 or less than -1, which are considered "bad" beta/psi values.
# The function generates a summary CSV file listing participant IDs with bad beta and/or psi files,
# along with detailed logs of the specific anomalies found.
####################################################################################################

from pathlib import Path
import re
import pandas as pd
##################################################################################
# Change folder paths as needed
folder_path = Path("your_input_folder_path/GIMME/output_indSEM_folder")
save_path = Path("your_output_path/indSEM_Refit_SubList")
##################################################################################

bad_sub_ids_dict = {}
detailed_logs = []
missing_files = []

# Regex patterns for Betas and Psi files
pattern_betas = re.compile(r"(csm14aff\d+_\d+|sub-\d+)Betas\.csv$")
pattern_psi = re.compile(r"(csm14aff\d+_\d+|sub-\d+)Psi\.csv$")

# Check for subfolders with the expected structure
for subfolder in folder_path.glob("*/individual"):

    matched_files = list(subfolder.glob("*.csv"))
    matched = False
    current_sub_issues = {}
    current_sub_id = None

    for csv_file in matched_files:
        sub_id = None
        file_type = None

        if pattern_betas.search(csv_file.name):
            sub_id = pattern_betas.search(csv_file.name).group(1)
            file_type = "beta"
        elif pattern_psi.search(csv_file.name):
            sub_id = pattern_psi.search(csv_file.name).group(1)
            file_type = "psi"

        if sub_id:
            current_sub_id = sub_id  # Save sub_id even if issues not found
            matched = True
            # print(f"Processing {file_type} file: {csv_file}")
            print(f"Checking participant {sub_id}...")

            df = pd.read_csv(csv_file)

            if file_type == "beta":
                df = df.loc[:, ~df.columns.str.contains("lag", case=False)]

            numeric_df = df.select_dtypes(include='number')
            bad_mask = (numeric_df > 1) | (numeric_df < -1)

            if bad_mask.any().any():
                print(f"  → bad {file_type} found")
                current_sub_issues[file_type] = True

                for row_idx, col in zip(*bad_mask.to_numpy().nonzero()):
                    column_name = numeric_df.columns[col]
                    value = numeric_df.iat[row_idx, col]
                    log_msg = f"    [row {row_idx}, column '{column_name}']: {value}"
                    print(log_msg)
                    detailed_logs.append(f"{sub_id} ({file_type}) - {log_msg}")
            else:
                print(f"  → {file_type} ok")

    if current_sub_id:
        bad_sub_ids_dict[current_sub_id] = {
            "bad_psi": current_sub_issues.get("psi", False),
            "bad_beta": current_sub_issues.get("beta", False),
        }

    if not matched:
        fallback_id_match = re.search(r"(csm14aff\d+_\d+|sub-\d+)", str(subfolder.parent.name))
        fallback_id = fallback_id_match.group(1) if fallback_id_match else subfolder.parent.name
        missing_files.append(fallback_id)
        print(f"  → No matching Psi or Beta file found for {fallback_id}")

# After all subfolder checks, filter out cases where both bad_psi and bad_beta are False
bad_sub_ids_dict = {sub_id: issues for sub_id, issues in bad_sub_ids_dict.items() if issues["bad_psi"] or issues["bad_beta"]}

# Save bad subIDs to CSV
bad_subids_df = pd.DataFrame.from_dict(bad_sub_ids_dict, orient='index')
bad_subids_df.index.name = 'sub_id'
bad_subids_df.reset_index(inplace=True)

bad_subids_df.to_csv(save_path / "bad_subIDs.csv", index=False)

# Save detailed log
log_path = save_path / "bad_file_details.txt"
with open(log_path, "w") as f:
    for log in detailed_logs:
        f.write(log + "\n")

# Save missing file list
missing_path = save_path / "missing_files.txt"
with open(missing_path, "w") as f:
    for m in missing_files:
        f.write(m + "\n")

print(f"\nDone. {len(bad_subids_df)} bad file(s) found.")
print(f"{len(missing_files)} missing file(s) recorded.")
