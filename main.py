import numpy as np
import io_snc
import plots
import corrections
import pandas as pd

# Read the detector files
acml_file_path = r'P:\02_QA Equipment\02_ArcCheck\05_Commissoning\03_NROAC\Dose Rate Dependence Fix\Test on script\13-Jun-2023-Plan7 6X.acm'
txt_file_path = r'P:\02_QA Equipment\02_ArcCheck\05_Commissoning\03_NROAC\Dose Rate Dependence Fix\Test on script\13-Jun-2023-Plan7 6X.txt'

frame_data_df, diode_data_df, bkrnd_and_calibration_df = io_snc.parse_acm_file(acml_file_path)
header_data = io_snc.parse_arccheck_header(txt_file_path)
array_data = io_snc.parse_arrays_from_file(txt_file_path)


# Get the intrinsic corrections from the txt file. This is the field size and angular correction applied
# by the SNC Patient software. This will be used at the end after we've calculated the dose rate corrected
# array of dose values we obtain from acm file.
intrinsic_corrections = corrections.get_intrinsic_corrections(array_data)
if intrinsic_corrections is not None:
    print("Intrinsic Corrections Array:")
    print(intrinsic_corrections)
else:
    print("Failed to calculate intrinsic corrections.")


# Subtract the background from diode_data_df
diode_data_df = diode_data_df.subtract(bkrnd_and_calibration_df.Background)

# Multiply the diode_data_df by the calibration factor
diode_data_df = diode_data_df.multiply(bkrnd_and_calibration_df.Calibration)


#file_path = 'output_snc_file.txt'
#io_snc.write_snc_txt_file(array_data, header_data, file_path)


# Correct the counts for background and detector sensitivity calibration factor
diode_data_df = diode_data_df.subtract(background_df.values)

# Dose per count calibration factor
# TODO: Get dose per count calibration factor from acl file directly.
dose_per_count: float = 7.7597E-06  # cGy/count

# Calculate the dose values
dose_accumulated_df = counts_accumulated_df * dose_per_count # cGy

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
dose_rate_arrays = io_snc.detector_arrays(dose_rate_df)

## This section is for the Jager pulse rate correction
# Jager pulse rate coefficients
# https://doi.org/10.1002/acm2.13409 figure 1
a_pr = 0.035
b_pr = 5.21*10**-5  # Corrected the exponentiation operator
c_pr = 1

jager_pr_coefficients = np.array([a_pr, b_pr, c_pr])

# Jager dose per pulse coefficients (MU/min)
# https://doi.org/10.1002/acm2.13409 figure 3
a_dpp = 0.0978
b_dpp = 3.33*10**-5  # Corrected the exponentiation operator
c_dpp = 1.0011

jager_dpp_coefficients = np.array([a_dpp, b_dpp, c_dpp])

pr_corrected_count_df = corrections.pulse_rate_correction(counts_accumulated_df, jager_pr_coefficients)
dpp_corrected_count_df = corrections.dose_per_pulse_correction(counts_accumulated_df, jager_dpp_coefficients)

pr_corrected_dose_df = pr_corrected_count_df * dose_per_count
dpp_corrected_dose_df = dpp_corrected_count_df * dose_per_count


# Create a list of detector arrays arranged in the SNC Patient display configuration
diode_numbers_in_snc_array = io_snc.diode_numbers_in_snc_array()
X= np.arange(-32.5, 33, 0.5)
Y = np.arange(10, -10.5, -0.5)

# Select a xn by yn square centered around detector number 61
# Step 1: Identify the indices of the 9 detectors
detector_number = 610
row, col = np.where(diode_numbers_in_snc_array == detector_number)  # Find the position of detector number 610
row, col = row[0], col[0]  # np.where returns arrays, so we take the first element

# Step 2: Calculate the half size of the square
xn = 31
yn = 15
half_xn = xn // 2
half_yn = yn // 2

# Step 3: Calculate the indices of the xn by yn square centered around the detector
start_row = row - half_yn if row - half_yn >= 0 else row
end_row = row + half_yn + 1 if row + half_yn + 1 <= diode_numbers_in_snc_array.shape[0] else row + 1
start_col = col - half_xn if col - half_xn >= 0 else col
end_col = col + half_xn + 1 if col + half_xn + 1 <= diode_numbers_in_snc_array.shape[1] else col + 1

startframe = 1550
endframe = 1600


selected_dose_rate_arrays = dose_rate_arrays[startframe:endframe, start_row:end_row, start_col:end_col]
selected_X = X[start_col:end_col]
selected_Y = Y[start_row:end_row]

# Create a gif animation of the dose rate over time for the selected range of detectors
plots.create_animation(dose_rate_arrays, xn, yn, detector_number)

plots.scatter_cumulative_dose(dose_rate_df[startframe:endframe], dose_accumulated_df[startframe:endframe],
                              detector_number)

plots.bar_doserate_histogram(dose_df, dose_rate_df, [630, 610, 590, 570, 550])


# TODO: Create a function to put the corrected dose values back into the .txt file
