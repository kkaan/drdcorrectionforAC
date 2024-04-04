import pandas as pd
import numpy as np

def read_detector_file(file_path):
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


# Usage
file_path = r'P:\02_QA Equipment\02_ArcCheck\05_Commissoning\03_NROAC\Dose Rate Dependence Fix\Test on script\13-Jun-2023-Plan7 6Xcropped.txt'
data_df, background, calibration_factor = read_detector_file(file_path)

#Correct the counts for background and detector sensitivity calibration factor
corrected_data = (data_df - background) * calibration_factor



# Calculate the difference between subsequent rows
differential_count = corrected_data.diff().shift(-1)

# The last row will be NaN because there's no subsequent row to subtract from, so you might want to drop it
differential_count = differential_count[:-1]

#dose per count calibration factor
dose_per_count: float = 7.7597E-06

dose_data = corrected_data*dose_per_count
diff_dose = differential_count*dose_per_count

# Display the first few rows of the data
print(data_df.head())

def detectorarray(diff_dose):

    # Assuming corrected_data_df is your DataFrame with corrected count values
    # Extract the first row of corrected count values
    first_row_counts = diff_dose.iloc[0].values

    # Create an initial array of size 41x131 filled with zeros
    array = np.zeros((41, 131))

    # Initialize the detector number to match the DataFrame's column indexing
    number = 1
    for row in range(40, -1, -2):  # Start from the last row, move upwards in steps of 2
        for col in range(0, 131, 2):  # Start from the first column, move right in steps of 2
            if number <= 1386:
                # Assign the count value corresponding to the detector number
                # Detector numbers correspond to DataFrame columns, assuming 1-based indexing
                array[row, col] = first_row_counts[number - 1]  # Adjust for 0-based indexing in the array
                number += 1
            else:
                break  # Stop if the number exceeds 1386


diffdosearray = detectorarray(diff_dose)

    # Display part of the array to check
print(diffdosearray[:5, :10])  # Adjust as needed to view different parts of the array