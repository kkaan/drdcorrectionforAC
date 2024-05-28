# Description:  This script reads a detector file and returns the data, background, and calibration factor.
#               It also rearranges the detector data from the acl file into the one displayed in SNC Patient.
#               The detector data is then saved as a .npz file.
# NOTE: Currently only takes in pre-formatted interim tab delimited file.

import numpy as np
import os
import pandas as pd

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
        'Applied Field Size': None, 'Applied Heterogeneity': None,
        'Full Header Text': ''
    }

    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()

        full_header_text = ""
        found_header = False
        for line in lines:
            if line.strip() == "Background":  # Check for delimiter before appending to header text
                break
            full_header_text += line
            key_value = line.split(':')
            if len(key_value) == 2:
                key, value = key_value[0].strip(), key_value[1].strip()
                if key in header_keys:
                    header_keys[key] = value
                    found_header = True

        # Strip the last newline character to clean up the header text
        header_keys['Full Header Text'] = full_header_text.rstrip()

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

    # Define the exact names of arrays expected in the file
    valid_arrays = [
        'Background', 'Calibration Factors', 'Offset', 'Raw Counts', 'Corrected Counts',
        'Dose Counts', 'Data Flags', 'Interpolated', 'Dose Interpolated',
        'Corrected Counts (No Angular Correction)'
    ]

    for line in lines:
        line = line.strip()
        # Check if the line matches any of the valid array names exactly
        if line in valid_arrays:
            if current_array is not None:
                # Handle conversion by ensuring all rows are the same length
                max_length = max(len(row) for row in array_content)
                uniform_content = [row + [None] * (max_length - len(row)) for row in array_content]
                array_data[current_array] = np.array(uniform_content, dtype=object)  # Use dtype=object for mixed types
            current_array = line
            array_content = []
        elif current_array is not None:  # Continue capturing data if we're within an array
            parsed_line = line.split()
            array_content.append(parsed_line)

    # Finalize the last array data capture
    if current_array is not None:
        max_length = max(len(row) for row in array_content)
        uniform_content = [row + [None] * (max_length - len(row)) for row in array_content]
        array_data[current_array] = np.array(uniform_content, dtype=object)

    return array_data

def write_snc_txt_file(array_data, header_data, file_path):
    """
    Writes the array data and header into a .txt file in the same format as it was read.
    Omits None values and uses tabs instead of spaces between array values.

    Parameters:
    - array_data (dict): Dictionary containing all the array data.
    - header_data (dict): Dictionary containing all the header information, including 'Full Header Text'.
    - file_path (str): Path to the file where the data should be saved.
    """
    try:
        with open(file_path, 'w') as file:
            # Write the full header text directly from the header_data dictionary
            if 'Full Header Text' in header_data:
                file.write(header_data['Full Header Text'])
                file.write("\n\n")  # Ensure there's a blank line after the header

            # Write each array, skipping None values and using tabs as delimiter
            for array_name, array_content in array_data.items():
                file.write(f"{array_name}\n")
                for row in array_content:
                    # Only write the row if it contains any non-None values
                    if any(x is not None for x in row):
                        row_data = '\t'.join(str(x) for x in row if x is not None)
                        # Add a tab character before 'COL' and 'Xcm'
                        row_data = row_data.replace('COL', '\tCOL').replace('Xcm', '\tXcm')
                        file.write(f"{row_data}\n")
                file.write("\n")  # Separate arrays by a newline for clarity

    except Exception as e:
        print(f"An error occurred while writing to file: {e}")

def parse_acm_file(file_path):
    frame_data_keys = [
        'UPDATE#', 'TIMETIC1', 'TIMETIC2', 'PULSES',
        'STATUS1', 'STATUS2', 'VirtualInclinometer', 'CorrectedAngle', 'FieldSize', 'Reference Diode'
    ]
    diode_data_keys = ['Reference Diode'] + [str(i) for i in range(1, 1387)]  # 1386 diodes

    # Initialize storage for frame data and diode data
    frame_data = []
    diode_data = []

    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Skip to line 77 where the data header starts
    data_header_index = 76  # 0-based index for line 77
    data_header = lines[data_header_index].strip().split('\t')

    # Extract Background and Calibration data
    background_data = lines[data_header_index + 1].strip().split('\t')[10:]  # Skip 'Background' line
    calibration_data = lines[data_header_index + 2].strip().split('\t')[10:]  # Skip 'Calibration' line

    # Create a DataFrame for Background and Calibration data
    bkrnd_and_calibration_df = pd.DataFrame({
        'Detector Names': diode_data_keys,
        'Background': background_data,
        'Calibration': calibration_data
    })

    # Process each line of data after the headers
    for line in lines[data_header_index + 3:]:  # Skip 'Background' and 'Calibration' lines
        row_data = line.strip().split('\t')
        if row_data[0] == 'Data:':  # Ensure we are reading a data line
            # Split frame data and diode data based on the known structure
            frame_row = row_data[1:len(frame_data_keys) + 1]
            diode_row = row_data[len(frame_data_keys) + 1:]
            frame_data.append(frame_row)
            diode_data.append(diode_row)

    # Convert lists to numpy arrays for easier manipulation later
    frame_data = np.array(frame_data, dtype=float)
    diode_data = np.array(diode_data, dtype=float)

    diode_data_keys = [str(i) for i in range(1, 1387)] # getting rid of the reference diodo key
    frame_data_df = pd.DataFrame(frame_data, columns=frame_data_keys)
    diode_data_df = pd.DataFrame(diode_data, columns=diode_data_keys)

    return frame_data_df, diode_data_df, bkrnd_and_calibration_df

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
