# Description:  This script reads a detector file and returns the data, background, and calibration factor.
#               It also rearranges the detector data from the acl file into the one displayed in SNC Patient.
#               The detector data is then saved as a .npz file.
# NOTE: Currently only takes in pre-formatted interim tab delimited file.
import pandas as pd
import numpy as np
import os

def parse_arccheck_header(file_path):
    if not os.path.exists(file_path):
        print(f"Error: The file {file_path} does not exist.")
        return None

    header_keys = {
        'FileName': None, 'Firmware Version': None, 'Hardware Revision': None, 'Diode Type': None,
        'Temperature': None, 'Inclinometer Tilt': None, 'Inclinometer Rotation': None,
        'Background Threshold': None, 'Measured Cavity Dose': None, 'Date': None, 'Time': None,
        'Serial No': None, 'Overrange Error': None, 'Cal File': None, 'Dose per Count': None,
        'Dose Info': None, 'Dose IDDC': None, 'Time': None, 'Orientation': None, 'Rows': None,
        'Cols': None, 'CAX X': None, 'CAX Y': None, 'Device Position QA': None, 'Shift X': None,
        'Shift Y': None, 'Shift Z': None, 'Rotation X': None, 'Rotation Y': None, 'Rotation Z': None,
        'Manufacturer': None, 'Energy': None, 'Plug Present': None, 'Applied Angular': None,
        'Applied Field Size': None, 'Applied Heterogeneity': None
    }

    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()

        found_header = False
        for line in lines:
            line = line.strip()
            if line == "Background":  # New delimiter to stop parsing header
                break
            key_value = line.split(':')
            if len(key_value) == 2:
                key, value = key_value[0].strip(), key_value[1].strip()
                if key in header_keys:
                    header_keys[key] = value
                    found_header = True

        if not found_header:
            print("Warning: No valid header information found.")
        else:
            print("Header information successfully parsed.")
        return header_keys

    except Exception as e:
        print(f"Error reading file: {e}")
        return None

def parse_arrays_from_file(file_path):
    array_data = {}
    current_array = None
    array_content = []

    with open(file_path, 'r') as file:
        lines = file.readlines()

    for line in lines:
        if any(name in line for name in ['Background', 'Calibration Factors', 'Offset', 'Raw Counts', 'Corrected Counts',
                                         'Dose Counts', 'Data Flags', 'Interpolated', 'Dose Interpolated',
                                         'Corrected Counts (No Angular Correction)']):
            if current_array is not None:
                # Handle conversion by ensuring all rows are the same length
                max_length = max(len(row) for row in array_content)
                uniform_content = [row + [None] * (max_length - len(row)) for row in array_content]
                array_data[current_array] = np.array(uniform_content, dtype=object)  # Use dtype=object for mixed types
            current_array = line.strip()
            array_content = []
        elif current_array is not None:
            parsed_line = line.split()
            array_content.append(parsed_line)

    if current_array is not None:
        max_length = max(len(row) for row in array_content)
        uniform_content = [row + [None] * (max_length - len(row)) for row in array_content]
        array_data[current_array] = np.array(uniform_content, dtype=object)

    return array_data

def write_snc_txt_file(array_data, header_data, file_path):
    """
    Writes the array data and header into a .txt file in the same format as it was read.

    Parameters:
    - array_data (dict): Dictionary containing all the array data.
    - header_data (dict): Dictionary containing all the header information.
    - file_path (str): Path to the file where the data should be saved.
    """
    try:
        with open(file_path, 'w') as file:
            # Write the header information
            for key, value in header_data.items():
                if value is not None:
                    file.write(f"{key}: {value}\n")
            file.write("\n")  # End of header part

            # Write each array
            for array_name, array_content in array_data.items():
                file.write(f"{array_name}\n")
                for row in array_content:
                    row_data = ' '.join(str(x) for x in row)
                    file.write(f"{row_data}\n")
                file.write("\n")  # Separate arrays by a newline for clarity

    except Exception as e:
        print(f"An error occurred while writing to file: {e}")

def read_acl_file(file_path):
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

def diode_numbers_in_snc_array():
    """
    Reorganizes the detectors numbers in an acl measurement file into the planar array
    that is displayed in SNC Patient software.

    Parameters:
    acl_file (str): The path to the acl measurement file.

    Returns:
    array (ndarray): A 2D numpy array representing the reorganized detectors.
    """
    # Step 1: Read the acl file and extract the detector numbers
    # This step is dependent on the format of the acl file and is not shown here

    # Step 2: Create an initial array of size 41x131 filled with zeros
    array = np.zeros((41, 131))

    # Step 3: Fill every second row and column with detector numbers
    # Starting from the bottom left corner (which in array indexing is the last row, first column)
    number = 1
    for row in range(40, -1, -2):  # Start from the last row, move upwards in steps of 2
        for col in range(0, 131, 2):  # Start from the first column, move right in steps of 2
            if number <= 1386:
                array[row, col] = number
                number += 1
            else:
                break  # Stop if the number exceeds 1386

    array = array.astype(int)
    return array

#TODO: Add functionality to read in raw data from acl file and format it into the correct format.
