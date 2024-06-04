import numpy as np
import os
import pandas as pd

def parse_arccheck_header(file_path):
    """
    Parses the header information from an ArcCheck file and returns it as a dictionary.

    Parameters
    ----------
    file_path : str
        The path to the ArcCheck file.

    Returns
    -------
    dict or None
        A dictionary containing header information if the file exists, otherwise None.
    """
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
        header_keys['Full Header Text'] = full_header_text.strip()

        return header_keys if found_header else None

    except Exception as e:
        print(f"Error parsing the header: {e}")
        return None

def parse_arccheck_data(file_path):
    """
    Parses the data section of an ArcCheck file into a pandas DataFrame.

    Parameters
    ----------
    file_path : str
        The path to the ArcCheck file.

    Returns
    -------
    pandas.DataFrame or None
        A DataFrame containing the parsed data if the file exists, otherwise None.
    """
    if not os.path.exists(file_path):
        print(f"Error: The file {file_path} does not exist.")
        return None

    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()

        # Skip header section
        data_lines = []
        header_finished = False
        for line in lines:
            if header_finished:
                data_lines.append(line.strip())
            if line.strip() == "Background":
                header_finished = True

        # Create a DataFrame from the data lines
        data = pd.DataFrame([x.split() for x in data_lines if x], dtype=float)
        return data

    except Exception as e:
        print(f"Error parsing the data: {e}")
        return None

def convert_arccheck_data_to_array(df):
    """
    Converts the ArcCheck data from a DataFrame to a 3D numpy array.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing the ArcCheck data.

    Returns
    -------
    numpy.ndarray
        3D numpy array with the data organized in the appropriate structure.
    """
    rows, cols = df.shape
    arrays = np.zeros((rows, 41, 131))

    for row_index in range(rows):
        current_row_counts = df.iloc[row_index].values

        # Initialize the detector number to match the DataFrame's column indexing
        number = 1
        for row in range(40, -1, -2):  # Start from the last row, move upwards in steps of 2
            for col in range(0, 131, -2):  # Start from the first column, move right in steps of 2
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

    Returns
    -------
    numpy.ndarray
        A 2D numpy array representing the reorganized detectors.
    """
    array = np.zeros((41, 131))

    number = 1
    for row in range(40, -1, -2):
        for col in range(0, 131, 2):
            if number <= 1386:
                array[row, col] = number
                number += 1
            else:
                break

    array = array.astype(int)
    return array
