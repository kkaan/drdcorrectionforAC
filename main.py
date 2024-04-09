import numpy as np
from read_acl_file import read_detector_file, detector_arrays
from plotdiodecounts import create_animation, create_cumulative_dose_animation, create_histogram


# Read the detector file
file_path = r'P:\02_QA Equipment\02_ArcCheck\05_Commissoning\03_NROAC\Dose Rate Dependence Fix\Test on script\13-Jun-2023-Plan7 6Xcropped.txt'
data_df, background, calibration_factor = read_detector_file(file_path)

# Correct the counts for background and detector sensitivity calibration factor
corrected_df = (data_df - background) * calibration_factor

# Calculate the difference between subsequent rows
corrected_count_diff_df = corrected_df.diff().shift(-1)
# The last row will be NaN because there's no subsequent row to subtract from, so we'll drop it.
corrected_count_diff_df = corrected_count_diff_df[:-1]

# Dose per count calibration factor
# TODO: Get dose per count calibration factor from acl file directly.
dose_per_count: float = 7.7597E-06  # cGy/count

# Calculate the dose values
dose_df = corrected_df * dose_per_count

# Calculate the dose rate values
# Assuming the time interval between each frame is 50 ms
time_interval = 50  # in milliseconds
dose_rate_df = corrected_count_diff_df * dose_per_count / time_interval


# Create a list of detector arrays frames from the dose rate DataFrame
# Each array represents a frame of the detector array at a specific time point
dose_rate_arrays = detector_arrays(dose_rate_df)
np.savez("diff_dose_arrays.npz", *dose_rate_arrays)

# Load the differential dose arrays
data = np.load("diff_dose_arrays.npz")
start_row = 1000  #
end_row = 1200  #

# Create the list of arrays for the specified range
loaded_dose_rate_arrays = [data[f"arr_{i}"] for i in range(start_row, end_row)]

# Alternatively, you can load all the arrays
diff_dose_arrays = [data[key] for key in data.keys()]

#jager function y=c-a.e^-bx
#a = 0.035
#b = 5.21*10^-5
#c = 1


# Call the functions
create_animation(diff_dose_arrays)
create_cumulative_dose_animation(detector_values)
create_histogram(detector_values)

#TODO: Add the code to display the animation
#TODO: Add the code to plot the cumulative dose over time for a selected detector
#TODO: Add the code to plot