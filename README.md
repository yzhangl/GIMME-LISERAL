# GIMME-LISERAL
Supporting python code for integrating LISERAL-based GIMME outputs to R-based outputs

## convertMatrix_commented.py
This file defines function to convert R csv output into liseral input binary matrices (0/1).

Input: R GIMME output CSV file with columns: lhs, op, rhs, beta, se, z, pval, level

Output: Two binary matrices (lag and non-lag) in a single txt file, where each row is the lag matrix row followed by non-lag matrix row

Note: Rows and columns correspond to specific brain regions defined in 'rows' dictionary

## convertMatrix_txtinput_commented.py
This file defines function that has similar utility as the previous one, except the input is now txt files for refitting from scratch.

Input: txt file with each line: lhs ~ rhs (indicating a path from lhs to rhs)

Output: Two binary matrices (lag and non-lag) in a single txt file (similar as above)

## liseral_AM_extract_commented.py
This python function searches through an automatic search (defined with the AM command) LISERAL GIMME output txt file for the FIRST excellent fitting model (defined as 2 out of 4 goodness of fit statistics meeting conventional criteria).
Once criteria is met, the function extracts:
1) a txt file of the beta estimates, in the original LISERAL format;
2) a csv file of the beta values, excluding lagged rows;
3) a csv file of the standard error values of betas, excluding lagged rows;
4) a csv file of the t-values of betas, excluding lagged rows;
5) a txt file of the LISERAL model in the binary 1/0 format so you can input that into another LISERAL model for further refitting if needed

Note, the current python file expects that the output txt file starts with "o" (e.g., "o10005.txt"). In this example, "10005" is the subid.

The script also loops through ALL output txt files in the directory folder, which is user-specified.

## liseral_single_extract_commented.py
An adapted version of the AM extract function above that extracts the relevant information from a single estimated GIMME model (i.e., no AM command used).

The user will need to specify the specific output file (e.g., "o10005.txt") and the directory in which you want the new extracted information to be saved. A new folder with the participant ID will be created within that directory.

The function extracts:
1) a csv file of the beta values, excluding lagged rows;
2) a csv file of the standard error values of betas, excluding lagged rows;
3) a csv file of the t-values of betas, excluding lagged rows;

## convert_LISERALbeta_to_resting_commented.py
This function converts the beta output files (in the same directory) extracted from LISERAL into a csv format that is compatible with the R GIMME package output format for further analysis.

This script is for converting regular GIMME outputs, not for indSEM outputs. Specifically, the difference is in how group-level and individual-level paths are defined.

The converted output csv file will contain columns:

'file' (original complex filename), 'ff_id' (extracted five-digit participant ID),'lhs', 'rhs', 'beta', 'level' (group or ind)

Note, the way ff_id is extracted assumes the original complex filename contains 'csm14aff' followed by the five-digit ID.

The user also should change the mapping of VAR codes to the specific names of ROIs that matches the R GIMME outputs.

## search_indSEM_betapsi_commented.py
This function searches through an indSEM GIMME output folder structure for beta and psi files that contain any values greater than 1 or less than -1, which are considered "bad" beta/psi values.

The function generates a summary CSV file listing participant IDs with bad beta and/or psi files, along with detailed logs of the specific anomalies found.
