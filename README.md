# GIMME-LISERAL
Supporting python code for integrating LISERAL-based GIMME outputs to R-based outputs

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
