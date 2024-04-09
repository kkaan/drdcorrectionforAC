from typing import Any

import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.colors import LinearSegmentedColormap



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

# Correct the counts for background and detector sensitivity calibration factor
corrected_data = (data_df - background) * calibration_factor

# Calculate the difference between subsequent rows
differential_count = corrected_data.diff().shift(-1)

# The last row will be NaN because there's no subsequent row to subtract from, so you might want to drop it
differential_count = differential_count[:-1]

#jager function y=c-a.e^-bx
a = 0.035
b = 5.21*10^-5
c = 1



# dose per count calibration factor
dose_per_count: float = 7.7597E-06

dose_data = corrected_data * dose_per_count
diff_dose = differential_count * dose_per_count


# Display the first few rows of the data
print(data_df.head())


def detector_arrays(diff_dose):
    arrays = []  # List to hold all the arrays

    for row_index in range(len(diff_dose)):
        # Extract the counts for the current row
        current_row_counts = diff_dose.iloc[row_index].values

        # Create an initial array of size 41x131 filled with zeros
        array = np.zeros((41, 131))

        # Initialize the detector number to match the DataFrame's column indexing
        number = 1
        for row in range(40, -1, -2):  # Start from the last row, move upwards in steps of 2
            for col in range(0, 131, 2):  # Start from the first column, move right in steps of 2
                if number <= 1386:
                    # Assign the count value corresponding to the detector number
                    array[row, col] = current_row_counts[number - 1]  # Adjust for 0-based indexing in the array
                    number += 1
                else:
                    break  # Stop if the number exceeds 1386

        arrays.append(array)  # Add the created array to the list

    return arrays

# Assuming diff_dose is your DataFrame with differential count values
diff_dose_arrays = detector_arrays(diff_dose)
np.savez("diff_dose_arrays.npz", *diff_dose_arrays)

data = np.load("diff_dose_arrays.npz")
diff_dose_arrays = [data[f"arr_{i}"] for i in range(len(data.files))]

# Display part of the array to check
first_array = diff_dose_arrays[0]

# Create a custom colormap
# Dark blue for values < 60, light blue for values between 60 and 100, and green for values > 100
# Create a custom colormap
cmap = LinearSegmentedColormap.from_list(
    'custom_blue_green',
    [(0, 'darkblue'), (0.6, 'darkblue'), (0.6, 'lightblue'), (1, 'lightblue'), (1, 'green')],
    N=256
)

# Normalize the array values to 0-1 range to match our custom colormap thresholds
norm = plt.Normalize(vmin=first_array.min(), vmax=first_array.max())
# Plotting the heatmap
plt.figure(figsize=(20, 10))
ax = sns.heatmap(first_array, cmap=cmap, norm=norm, cbar_kws={'label': 'Differential Count'}, square=True,
                 xticklabels=50, yticklabels=50)  # Setting up for custom tick labels

# Adjusting the ticks to represent the new ranges
# Calculating the new tick positions and labels based on the specified cm spacing
xticks = np.linspace(0, first_array.shape[1], num=11)  # 11 ticks from -32.5 to 32.5, including the center at 0
yticks = np.linspace(0, first_array.shape[0], num=5)  # 5 ticks from 10 to -10, including the center at 0

# Calculating the new tick labels
xticklabels = [f"{x-32.5}" for x in np.linspace(0, 65, num=11)]
yticklabels = [f"{10-x*10}" for x in np.linspace(0, 2, num=5)]

# Applying the new ticks and labels to the plot
ax.set_xticks(xticks)
ax.set_yticks(yticks)
ax.set_xticklabels(xticklabels)
ax.set_yticklabels(yticklabels)

plt.xlabel('X (cm)')
plt.ylabel('Y (cm)')
plt.title('Differential Dose Distribution')

# Save the figure to a file
plt.savefig("differential_count_distribution_adjusted.png", dpi=300)  # Save as a PNG file with high resolution

plt.show()  # Show the plot as the last step

