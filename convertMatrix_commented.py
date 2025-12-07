###################################################################################################
####### Define function to convert R csv output into liseral input binary matrices (0/1) ##########
#    Input: CSV file with columns: lhs, op, rhs, beta, se, z, pval, level
#    Output: Two binary matrices (lag and non-lag) in a single txt file
#            Each row: lag matrix row followed by non-lag matrix row
#    Note: Rows and columns correspond to specific brain regions defined in 'rows' dictionary
####################################################################################################

"""A simple python script template.
"""

import os
import glob
import sys
import argparse
import pandas as pd
import collections as cl


def main(arguments):
    ############################################################################
    # Read input csv file, edit as needed
    filename = 'your_input_folder/your_paths.csv'
    ############################################################################

    id = filename[54:59]
    print(id)

    try:
        df = pd.read_csv(filename, usecols = ['file', 'lhs', "op", "rhs", "beta", "se", 'z', "pval", "level"])
    except:
        print(f"file missing columns {filename}")

    # drop all other column
    df = df.drop('file', axis=1)
    df = df.drop('op', axis=1)
    df = df.drop('beta', axis=1)
    df = df.drop('se', axis=1)
    df = df.drop('z', axis=1)
    df = df.drop('pval', axis=1)
    df = df.drop('level', axis=1)
    
    # Define the row names (and col names are the same)
    rows = {'DMN_1':0,'DMN_2':1,'DMN_3':2,'DMN_4':3,'DMN_5':4,'DMN_6':5,'SAL_1':6,'SAL_2':7,'SAL_3':8,'SAL_4':9,'SAL_5':10,'SAL_6':11,'FPN_1':12,'FPN_2':13,'FPN_3':14,'FPN_4':15,'FPN_5':16,'FPN_6':17}
    
    # Create empty matrices
    matrix = [[0 for i in range(18)] for j in range(18)]
    matrix_lag = [[0 for i in range(18)] for j in range(18)]

    # Loop for each input, replace with 1
    for index,row in df.iterrows():
        lhs = row['lhs'].strip()
        rhs = row['rhs'].strip()
        is_lag = False

        if 'lag' in rhs:
            is_lag = True
            rhs = rhs[:-3]
        
        lhs_idx = rows[lhs]
        rhs_idx = rows[rhs]

        if is_lag:
            matrix_lag[lhs_idx][rhs_idx] = 1
        else:
            matrix[lhs_idx][rhs_idx] = 1

    ############################################################################
    # Read input csv file, edit as needed
    # Write into txt file
    filename = id+'_matrix.txt'
    with open("your_output_folder/"+filename, "w") as file:
    ############################################################################

      for i in range(len(matrix)):
        
            total_data_string_matrix = '  '.join(str(x) for x in matrix[i])
            total_data_string_matrix_lag = '  '.join(str(x) for x in matrix_lag[i])
            file.write(f"{total_data_string_matrix_lag}    {total_data_string_matrix}"+'\n')
    
    return

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
