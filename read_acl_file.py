# Description:  This script reads a detector file and returns the data, background, and calibration factor.
#               It also rearranges the detector data from the acl file into the one displayed in SNC Patient.
#               The detector data is then saved as a .npz file.
# NOTE: Currently only takes in pre-formatted interim tab delimited file.
import pandas as pd
import numpy as np

def read_detector_file(file_path):
    """
    Reads a detector file and returns the data, background, and calibration factor.

    Parameters:
    acml_file_path (str): The path to the detector file.

    Returns:
    data (DataFrame): The data from the detector file.
    background (array): The background values from the detector file.
    calibration_factor (array): The calibration factor values from the detector file.
    """
    # Read the header row for column names
    col_names = pd.read_csv(file_path, sep='\t', nrows=0).columns

    # Read the 'background' and 'calibration factor' rows
    metadata = pd.read_csv(file_path, sep='\t', nrows=2, skiprows=[0], header=None)
    background = metadata.iloc[0, :].values
    calibration_factor = metadata.iloc[1, :].values

    # Read the actual count data, skipping the first three rows
    data = pd.read_csv(file_path, sep='\t', skiprows=3, names=col_names)

    # Optionally, add background and calibration factor to the DataFrame if needed
    # For example, as additional columns, or you could adjust based on your needs.

    return data, background, calibration_factor

def detector_arrays(acl_detectors):
    """
    Rearranges the detector data from acl file into the one displayed in SNC Patient.

    Parameters:
    acl_detectors (DataFrame): The measurement data arranged in acl formal.

    Returns:
    arrays (ndarray): A 3D numpy array created from the differential dose data.
    """
    # Initialize a 3D numpy array with zeros
    arrays = np.zeros((len(acl_detectors), 41, 131))

    for row_index in range(len(acl_detectors)):
        # Extract the counts for the current row
        current_row_counts = acl_detectors.iloc[row_index].values

        # Initialize the detector number to match the DataFrame's column indexing
        number = 1
        for row in range(40, -1, -2):  # Start from the last row, move upwards in steps of 2
            for col in range(0, 131, 2):  # Start from the first column, move right in steps of 2
                if number <= 1386:
                    # Assign the count value corresponding to the detector number
                    arrays[row_index, row, col] = current_row_counts[number - 1]  # Adjust for 0-based indexing in the array
                    number += 1
                else:
                    break  # Stop if the number exceeds 1386

    return arrays


#TODO: Add functionality to read in raw data from acl file and format it into the correct format.
