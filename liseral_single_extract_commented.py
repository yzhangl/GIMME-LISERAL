###################################################################################################
######### Define functions to extract liseral output with single estimation (txt file) ############
# This function is an adapted version of the liseral_AM_extract_commented.py script
# Instead of extracting from multiple output files, this function extracts from a single output file 
#
# The current function assumes that your output file is named starting with "o" (e.g., o10005.txt)
# 
# This script also loops through ALL the output txt files in your directory folder (specified below)
#
# Here, we save several things based on the extracted model: 
# 1) a csv file of the beta values, excluding lagged rows; 
# 2) a csv file of the standard error values of betas, excluding lagged rows; 
# 3) a csv file of the t values of betas, excluding lagged rows; 
####################################################################################################

import re
import numpy as np
import pandas as pd
import os

def extract_five_digit_number(s):
    """
    Extracts a 5-digit number from the input string.
    Returns the number as an integer if found, otherwise None.
    """
    match = re.search(r'\d{5}', s)
    if match:
        return int(match.group(0))
    return None

def extract_lisrel_section(input_file, output_file):
    with open(input_file, 'r', encoding='ISO-8859-1') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        extracting = False
        for line in infile:
            if "LISREL Estimates (Maximum Likelihood)" in line:
                extracting = True
            if "Covariance Matrix of ETA" in line and extracting:
                break
            if extracting:
                outfile.write(line)

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

######################## EDIT ##################################
# Specify the input path of the specific LISERAL output txt file
input_path = "user_specified_path/output_file.txt"
################################################################

participant_name = extract_five_digit_number(input_path)

######################## EDIT ##################################
# Specify the output path of the specific LISERAL output txt file
output_path = "extracted_lisrel.txt"
################################################################
extract_lisrel_section(input_path, output_path)

# Read the content of the file.
with open('extracted_lisrel.txt', 'r') as file:
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
            
                            # v2 = parse_token(vals2[j]) if j < len(vals2) else np.nan
                # v3 = parse_token(vals3[j]) if j < len(vals3) else np.nan
                
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

# Replace all NaN values with 0
first_values = first_values.fillna(0)
second_values = second_values.fillna(0)
third_values = third_values.fillna(0)

# Write each to a separate CSV file.
first_values.to_csv(f"{participant_name}_beta.csv")
second_values.to_csv(f"{participant_name}_se.csv")
third_values.to_csv(f"{participant_name}_tval.csv")

file_path = "extracted_lisrel.txt"

if os.path.exists(file_path):
    os.remove(file_path)
    print(f"File '{file_path}' has been removed successfully.")
else:
    print(f"File '{file_path}' does not exist.")