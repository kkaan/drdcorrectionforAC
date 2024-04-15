import numpy as np
from read_acl_file import read_detector_file, detector_arrays
import plots
from diode_numbers_in_snc_array import diode_numbers_in_snc_array

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
dose_accumulated_df = dose_accumulated_df[1:]   # Matching the length of dose_df

# Calculate the dose rate values
# Assuming the time interval between each frame is 50 ms
time_interval = 50/60000  # in minutes
dose_rate_df = dose_df / time_interval # cGy/min


# Create a list of detector arrays arranged in the SNC Patient display configuration
# Each array represents a frame of the detector array at a specific time point
dose_rate_arrays = detector_arrays(dose_rate_df)


#jager function y=c-a.e^-bx
#a = 0.035
#b = 5.21*10^-5
#c = 1


diode_numbers_in_snc_array = diode_numbers_in_snc_array()

# Step 1: Identify the indices of the 9 detectors
detector_number = 610
row, col = np.where(diode_numbers_in_snc_array == detector_number)  # Find the position of detector number 610
row, col = row[0], col[0]  # np.where returns arrays, so we take the first element

# Calculate the half size of the square
xn = 31
yn = 15
half_xn = xn // 2
half_yn = yn // 2

# Calculate the indices of the xn by yn square centered around the detector
start_row = row - half_yn if row - half_yn >= 0 else row
end_row = row + half_yn + 1 if row + half_yn + 1 <= diode_numbers_in_snc_array.shape[0] else row + 1
start_col = col - half_xn if col - half_xn >= 0 else col
end_col = col + half_xn + 1 if col + half_xn + 1 <= diode_numbers_in_snc_array.shape[1] else col + 1

startframe = 1500
endframe = 1700


selected_dose_rate_arrays = dose_rate_arrays[startframe:endframe, start_row:end_row, start_col:end_col]

# Create a gif animation of the dose rate over time for the selected range of detectors
#create_animation(selected_dose_rate_arrays, xn, yn, detector_number)

plots.scatter_cumulative_dose(dose_rate_df[startframe:endframe], dose_accumulated_df[startframe:endframe],
                              detector_number)

plots.bar_doserate_histogram(dose_df, dose_rate_df, [630, 610, 590, 570, 550])

#TODO: Add the code to display the animation
#TODO: Add the code to plot the cumulative dose over time for a selected detector
#TODO: Add the code to plot