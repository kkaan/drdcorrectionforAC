import pandas as pd
import numpy as np

# Read detector labels and corresponding values from CSV
csv_file_path = r"P:\02_QA Equipment\02_ArcCheck\05_Commissoning\03_NROAC\Dose Rate Dependence Fix\Test on script\findingcoords.csv"
txt_file_path = r"P:\02_QA Equipment\02_ArcCheck\05_Commissoning\03_NROAC\Dose Rate Dependence Fix\Test on script\13-Jun-2023-Plan7 6X.txt"

# Read the CSV file to get calibration values
csv_data = pd.read_csv(csv_file_path, header=None)
#csv_data = csv_data.T

# Assuming the third column contains the calibration values (skipping the first two columns)
#calibration_values_csv = csv_data.iloc[:, 2].round(6)  # Round calibration values to 6 decimal places
calibration_values_csv = csv_data.iloc[2].round(6)

def read_spatial_arrangement(file_path, start_row, end_row, start_col):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        # Extracting the relevant lines based on provided start and end rows
        relevant_lines = lines[start_row-1:end_row]  # Adjusting for 0-based index
        # Converting lines to a 2D list (array), starting from the specified column to exclude y position and row number
        array = [list(map(float, line.split()[start_col:])) for line in relevant_lines]
        return np.array(array)

# Adjusted function to read only calibration values, starting from the third column (index 2)
calibration_values = read_spatial_arrangement(txt_file_path, 103, 143, 2)

# Read calibration values from the TXT file
calibration_values_txt = read_spatial_arrangement(txt_file_path, 103, 143, 2)  # Adjusted to start from the third column

def map_detectors_to_positions(calibration_values_csv, calibration_values_txt):
    detector_positions = {}
    # Generate a list of detector labels based on the expected count
    detector_labels = list(range(0, calibration_values_csv.shape[0]+  1))

    # Iterate through the TXT calibration values
    for y in range(calibration_values_txt.shape[0]):
        for x in range(calibration_values_txt.shape[1]):
            cal_value = round(calibration_values_txt[y, x], 6)  # Round to match CSV precision

            # Find the index (position in CSV) of the calibration value that matches
            # This assumes each calibration value is unique to each detector
            match_index = calibration_values_csv[calibration_values_csv == cal_value].index
            if not match_index.empty:  # If a match is found
                detector_label = detector_labels[match_index[0]]  # Get the corresponding detector label
                detector_positions[detector_label] = (x, y)  # Map detector label to its position

    return detector_positions

# Execute the function to map detectors
detector_positions = map_detectors_to_positions(calibration_values_csv, calibration_values_txt)

# Assuming 'detector_positions' is a dictionary with detector labels as keys
# and (x, y) tuples as values from the previous mapping process

# Determine the size of the array needed
max_x = max(pos[0] for pos in detector_positions.values()) + 1  # Adding 1 because Python indexing starts at 0
max_y = max(pos[1] for pos in detector_positions.values()) + 1  # Adding 1 for the same reason

# Initialize an empty array with a placeholder value (e.g., None or 0)
# Use None if you want to explicitly indicate "no detector"
detector_array = np.full((max_y, max_x), None)  # Notice the order is (max_y, max_x) because NumPy arrays are row-major

# Populate the array with detector labels
for label, (x, y) in detector_positions.items():
    detector_array[y, x] = label  # Assigning the detector label to the corresponding position

# Replace None with 0
detector_array = np.where(detector_array == None, 0, detector_array)
detector_array = detector_array.astype(int)
print(detector_array)

np.savetxt("detector_array.csv", detector_array, delimiter=",", fmt='%d')

