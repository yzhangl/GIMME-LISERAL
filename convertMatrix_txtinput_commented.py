###################################################################################################
####### Define function to convert GIMME txt files into liseral input binary matrices (0/1) #######
#    Input: txt file with each line: lhs ~ rhs (indicating a path from lhs to rhs)
#    Output: Two binary matrices (lag and non-lag) in a single txt file
#            Each row: lag matrix row followed by non-lag matrix row
#    Note: Rows and columns correspond to specific brain regions defined in 'rows' dictionary
# Typically used when you have to start refitting from the base indSEM model (i.e., from scratch)
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
    # Read input txt file, edit as needed
    filename = 'your_folder/your_paths.txt'
    id = filename[62:67]
    print(id)
    ############################################################################

    lefts = []
    rights = []

    try:
        f = open(filename, "r")
        for x in f:
            line = x
            line = line.strip()
            [left,right] = line.split(" ~ ")
            lefts.append(left)
            rights.append(right)
    except:
        print(f"file missing columns {filename}")
    
    print(lefts)
    print(rights)
    
    # Define the row names (and col names are the same)
    rows = {'DMN_1':0,'DMN_2':1,'DMN_3':2,'DMN_4':3,'DMN_5':4,'DMN_6':5,'SAL_1':6,'SAL_2':7,'SAL_3':8,'SAL_4':9,'SAL_5':10,'SAL_6':11,'FPN_1':12,'FPN_2':13,'FPN_3':14,'FPN_4':15,'FPN_5':16,'FPN_6':17}
    
    # Create empty matrices
    matrix = [[0 for i in range(18)] for j in range(18)]
    matrix_lag = [[0 for i in range(18)] for j in range(18)]

    for i in range(len(lefts)):
        lhs = lefts[i]
        rhs = rights[i]
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
        
    # print(matrix_lag)
    for i in range(len(matrix_lag)):
        matrix_lag[i][i] = 1


    ############################################################################
    # Read input txt file, edit as needed
    # Write into txt file
    filename = id+'_matrix_facespaths_restingMRI_fromscratch.txt'
    with open("./InputMatrix/"+filename, "w") as file:
    ############################################################################

      for i in range(len(matrix)):
        
            total_data_string_matrix = '  '.join(str(x) for x in matrix[i])
            total_data_string_matrix_lag = '  '.join(str(x) for x in matrix_lag[i])
            file.write(f"{total_data_string_matrix_lag}    {total_data_string_matrix}"+'\n')
    
    return

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
