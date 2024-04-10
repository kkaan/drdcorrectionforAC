import numpy as np
from read_acl_file import read_detector_file, detector_arrays
from plots import create_animation, create_cumulative_dose_animation


# Read the detector file
file_path = r'P:\02_QA Equipment\02_ArcCheck\05_Commissoning\03_NROAC\Dose Rate Dependence Fix\Test on script\13-Jun-2023-Plan7 6Xcropped.txt'
data_df, background, calibration_factor = read_detector_file(file_path)

# Correct the counts for background and detector sensitivity calibration factor
corrected_df = (data_df - background) * calibration_factor

# Dose per count calibration factor
# TODO: Get dose per count calibration factor from acl file directly.
dose_per_count: float = 7.7597E-06  # cGy/count

# Calculate the dose values
dose_accumulated_df = corrected_df * dose_per_count # cGy

# Calculate the difference between current row and previous row
dose_df = dose_accumulated_df.diff()    # cGy
dose_df = dose_df[1:]   # The first row will be NaNDrop the first row

# Calculate the dose rate values
# Assuming the time interval between each frame is 50 ms
time_interval = 50/60000  # in minutes
dose_rate_df = dose_df / time_interval # cGy/min


# Create a list of detector arrays arranged in the SNC Patient display configuration
# Each array represents a frame of the detector array at a specific time point
dose_rate_arrays = detector_arrays(dose_rate_df)
np.savez("dose_rate_arrays.npz", *dose_rate_arrays)

dose_arrays = detector_arrays(dose_df)
np.savez("dose_arrays.npz", *dose_rate_arrays)

# Load the differential dose arrays
data = np.load("dose_rate_arrays.npz")
start_row = 1000  #
end_row = 1200  #

test commit
# Create the list of arrays for the specified range
#dose_rate_arrays_saved = [data[f"arr_{i}"] for i in range(start_row, end_row)]

# Alternatively, you can load all the arrays
#diff_dose_arrays = [data[key] for key in data.keys()]

#jager function y=c-a.e^-bx
#a = 0.035
#b = 5.21*10^-5
#c = 1

# Create a gif animation of the dose rate over time for the selected range of detectors
#create_animation(dose_rate_arrays_saved)

create_cumulative_dose_animation(dose_rate_df, dose_accumulated_df, 610, 1500, 1700)
#create_histogram(dose_rate_df, dose_accumulated_df)

#TODO: Add the code to display the animation
#TODO: Add the code to plot the cumulative dose over time for a selected detector
#TODO: Add the code to plot