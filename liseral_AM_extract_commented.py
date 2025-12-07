###################################################################################################
######### Define functions to extract liseral output with automatic search (txt file) #############
# This function searches for the line "LISERAL Estimates (Maximum Likelihood)", which exists at 
# the beginning of each iteration of GIMME run. This function assumes the Automatic Search
# function is being used, therefore loops through the file to find the FIRST excellent fitting 
# model (current criteria: 2 out of 4 goodness of fit statistics meets the standard)
# Once the criteria is met, we will extract relevant information from the model into several files. 
#
# The current function assumes that your output file is named starting with "o" (e.g., o10005.txt)
# 
# This script also loops through ALL the output txt files in your directory folder (specified below)
#
# Here, we save several things based on the extracted model: 
# 1) a txt file of the beta estimates LISERAL model that was extracted, in the LISERAL format;
# 2) a csv file of the beta values, excluding lagged rows; 
# 3) a csv file of the standard error values of betas, excluding lagged rows; 
# 4) a csv file of the t values of betas, excluding lagged rows; 
# 5) a txt file of the LISERAL model in the 1/0 format to be inputted into the next LISERAL model 
# for further refitting
####################################################################################################

import re
import numpy as np
import pandas as pd
import os

def extract_lisrel_section(file_path, output_file):
    with open(file_path, 'r', encoding='ISO-8859-1') as file:
        lines = file.readlines()
    
    extract = False
    section = []
    last_lisrel_index = None
    rmsea_value = None
    nnfi_value = None
    cfi_value = None
    srmr_value = None
    should_break = False
    
    for i, line in enumerate(lines):
        if "LISREL Estimates (Maximum Likelihood)" in line:
            last_lisrel_index = i
        
        if "Goodness of Fit Statistics" in line:
            for j in range(i + 1, len(lines)):
                if "LISREL Estimates (Maximum Likelihood)" in lines[j]:
                    break  # Stop iterating when the next "LISREL Estimates (Maximum Likelihood)" is found
                if "Root Mean Square Error of Approximation (RMSEA)" in lines[j]:
                    rmsea_value = lines[j].strip().split()[-1]  # Extract last element as value after stripping spaces
                    rmsea_value = float(rmsea_value)
                if "Non-Normed Fit Index (NNFI)" in lines[j]:
                    nnfi_value = lines[j].strip().split()[-1]  # Extract last element as value after stripping spaces
                    nnfi_value = float(nnfi_value)
                if "Comparative Fit Index (CFI)" in lines[j]:
                    cfi_value = lines[j].strip().split()[-1]  # Extract last element as value after stripping spaces
                    cfi_value = float(cfi_value)
                if "Standardized RMR" in lines[j]:
                    srmr_value = lines[j].strip().split()[-1]  # Extract last element as value after stripping spaces
                    srmr_value = float(srmr_value)

                criteria = 0
                if rmsea_value and rmsea_value <= 0.05:
                    criteria += 1
                if nnfi_value and nnfi_value >= 0.95:
                    criteria += 1
                if cfi_value and cfi_value >= 0.95:
                    criteria += 1
                if srmr_value and srmr_value <= 0.05:
                    criteria += 1

                if criteria >= 2:
                    should_break = True
                    print("We found a model with excellent fit for participant=", file_path, " criteria=", criteria, " rmsea=", rmsea_value, " nnfi=", nnfi_value, " cfi=", cfi_value, " srmr=", srmr_value, " model starts on line=", last_lisrel_index)
                    break
            
            if should_break:
                break
    if not should_break:
        print("We did not find a model with excellent fit for participant=", file_path, " criteria=", criteria, " rmsea=", rmsea_value, " nnfi=", nnfi_value, " cfi=", cfi_value, " srmr=", srmr_value, " extracted the final model starting on line=", last_lisrel_index)

    if last_lisrel_index is not None:
        section = []
        for j in range(last_lisrel_index + 1, len(lines)):
            if "Covariance Matrix of ETA" in lines[j]:
                break
            section.append(lines[j])
    
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for line in section:
            outfile.write(line)

# Function to extract subID, expects that file name starts with "o", followed by subID
def extract_number_and_text(filename):
    match = re.match(r"o(\d{5})([a-zA-Z]*)\.txt", filename)
    if match:
        return match.group(1), match.group(2)
    return None, None

# Function to strip white spaces and parentheses due to LISERAL output formatting
def parse_token(token):
    """
    Remove surrounding whitespace and parentheses.
    Convert the token to a float if possible; otherwise, return np.nan.
    """
    token = token.strip()
    if token in ['- -', '--', '']:
        return np.nan
    token = token.strip("()")
    try:
        return float(token)
    except ValueError:
        return np.nan

################################ MODIFY HERE ####################################
############# Switch to location of YOUR liseral output file ####################
folder_path = "/Users/Insert/Your/Liseral/Output/File/Path/Here"
#################################################################################

# Iterate through all items in the folder
for item_name in os.listdir(folder_path):
    item_path = os.path.join(folder_path, item_name)
    
    if item_path.endswith(".txt") and os.path.isfile(item_path):
        # Process file
        print(f"File: {item_path}")

        # Example usage
        input_path = item_path
        subfile_name = item_path.split("/")[-1]
        participant_id, participant_suffix = extract_number_and_text(subfile_name)
        ################################ MODIFY HERE ####################################
        ############# Switch to location of YOUR liseral output file ####################
        os.makedirs(f"/Users/Insert/Your/Liseral/Output/File/Path/Here/{participant_id}", exist_ok=True)
        output_path = f"/Users/Insert/Your/Liseral/Output/File/Path/Here/{participant_id}/{participant_id}_replace_with_your_file_name.txt"
        #################################################################################
        extract_lisrel_section(input_path, output_path)

        ###### Here begins key function of extracting information from LISERAL formatted models ######
        
        # Read the content of the file.
        with open(output_path, 'r') as file:
            raw_text = file.read()

        # Create an empty 36x36 matrix that will hold a triple for each cell.
        matrix = np.empty((36, 36), dtype=object)
        # Initialize each cell with a default triple.
        for i in range(36):
            for j in range(36):
                matrix[i, j] = (np.nan, np.nan, np.nan)

        # Split the text into blocks using "BETA" as a delimiter.
        blocks = re.split(r'\n\s*BETA\s*\n', raw_text)[1:]

        # Process each block.
        for block in blocks:
            lines = block.splitlines()
            # Find the first nonempty line which should be the header.
            header_line = next((line for line in lines if line.strip()), None)
            if header_line is None:
                continue
            # Extract column variable names (e.g., "VAR 1", "VAR 2", …)
            col_names = re.findall(r'VAR\s+\d+', header_line)
            
            # Use a while-loop with an index so we can look ahead.
            i = lines.index(header_line) + 1  # start after the header

            while i < len(lines):
                line = lines[i]
                # print("@@@@@@@@@@@@@@ahh", line)
                increment = 0
                # Check if the line starts with a row label (e.g., "VAR 19")
                if re.match(r'^\s*VAR\s+\d+', line):
                    # This is the first line of a row group.
                    tokens1 = re.split(r'\s{2,}', line.strip())
                    row_label = tokens1[0]  # e.g., "VAR 19"
                    row_num = int(re.search(r'\d+', row_label).group()) - 1
                    vals1 = tokens1[1:]
                    vals2 = []
                    vals3 = []
                    if not all(x == "- -" for x in vals1):
                        # Try to get the next line as the second part of the triple.
                        if i + 1 < len(lines):
                            tokens2 = re.split(r'\s{2,}', lines[i+1].strip())
                            vals2 = tokens2
                            # increment += 1
                            # print("VALS", row_num, tokens2)
                            # i += 1  # skip this line as it's been processed
                        # Try to get the next line as the third part of the triple.
                        if i + 2 < len(lines):
                            tokens3 = re.split(r'\s{2,}', lines[i+2].strip())
                            # print(tokens3)
                            # print("TOKESNS", tokens3)
                            vals3 = tokens3
                            # increment += 1
                            # i += 1  # skip this line as well
                    
                    # For each column, assign a triple value. vals1 is always sparse and vals2 and vals3 are dense arrays.
                    for j in range(len(vals1)):
                        if j >= len(col_names):
                            continue
                        col_label = col_names[j]
                        col_num = int(re.search(r'\d+', col_label).group()) - 1
                        # Parse each of the tokens for the three values.
                        v1 = parse_token(vals1[j])
                        v2 = np.nan
                        v3 = np.nan
                        if not v1 is np.nan and vals2 and vals3:
                            v2 = vals2.pop(0)
                            # remove the left and right paren which are always there
                            v2 = v2[1:-1]
                            v3 = vals3.pop(0)
                        matrix[row_num, col_num] = (v1, v2, v3)
                        
                i += 1 # move to the next line

        # Create row and column labels ("VAR 1" ... "VAR 36")
        var_names = [f"VAR {i}" for i in range(1, 37)]
        df = pd.DataFrame(matrix, index=var_names, columns=var_names)

        # Extract the first, second, and third values from each tuple.
        first_values = df.applymap(lambda x: x[0] if isinstance(x, tuple) else x)
        second_values = df.applymap(lambda x: x[1] if isinstance(x, tuple) else x)
        third_values = df.applymap(lambda x: x[2] if isinstance(x, tuple) else x)

        # Drop the first 18 rows
        first_values = first_values.iloc[18:]
        second_values = second_values.iloc[18:]
        third_values = third_values.iloc[18:]

        # Create 0/1 input matrix
        bin_matrix = first_values.copy()
        bin_matrix = bin_matrix.astype(float)
        bin_matrix = bin_matrix.applymap(lambda x: 1 if not pd.isna(x) else 0)
        bin_matrix = bin_matrix.astype(int)

        # Replace all NaN values with 0
        first_values = first_values.fillna(0)
        second_values = second_values.fillna(0)
        third_values = third_values.fillna(0)

        # Write each to a separate CSV file.
        ################################ MODIFY HERE ####################################
        ######Switch to location where you want the extracted files to be saved #########
        first_values.to_csv(f"/Users/Insert/Your/Preferred/Saving/Location/Path/Here/{participant_id}/{participant_id}_beta.csv")
        second_values.to_csv(f"/Users/Insert/Your/Preferred/Saving/Location/Path/Here/{participant_id}/{participant_id}_se.csv")
        third_values.to_csv(f"/Users/Insert/Your/Preferred/Saving/Location/Path/Here/{participant_id}/{participant_id}_tval.csv")

        ## Convert DataFrame to formatted text
        with open(f"/Users/Insert/Your/Preferred/Saving/Location/Path/Here/{participant_id}/{participant_id}_extractedAM_matrix.txt", "w") as f:
            for row in bin_matrix.itertuples(index=False):
                row_str = "  ".join(str(row[i]) + ("  " if i == 17 else "") for i in range(len(row)))
                f.write(row_str + "\n")