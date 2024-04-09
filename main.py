from read_acl_file import read_detector_file, detector_arrays
from display_doserate_array_animation import display_doserate_array_animation
import numpy as np

# Read the detector file
file_path = r'P:\02_QA Equipment\02_ArcCheck\05_Commissoning\03_NROAC\Dose Rate Dependence Fix\Test on script\13-Jun-2023-Plan7 6Xcropped.txt'
data_df, background, calibration_factor = read_detector_file(file_path)




data = np.load("diff_dose_arrays.npz")
start_row = 1000  #
end_row = 1200  #

# Create the list of arrays for the specified range
diff_dose_arrays = [data[f"arr_{i}"] for i in range(start_row, end_row)]

diff_dose_arrays = [data[key] for key in data.keys()]

# Correct the counts for background and detector sensitivity calibration factor
corrected_data = (data_df - background) * calibration_factor

#jager function y=c-a.e^-bx
#a = 0.035
#b = 5.21*10^-5
#c = 1

# dose per count calibration factor
dose_per_count: float = 7.7597E-06


# Calculate the difference between subsequent rows
differential_count = corrected_data.diff().shift(-1)
# The last row will be NaN because there's no subsequent row to subtract from, so we'll drop it.
differential_count = differential_count[:-1]

dose_data = corrected_data * dose_per_count
diff_dose = differential_count * dose_per_count

# Assuming diff_dose is your DataFrame with differential count values
diff_dose_arrays = detector_arrays(diff_dose)
np.savez("diff_dose_arrays.npz", *diff_dose_arrays)

#TODO: Add the code to display the animation
#TODO: Add the code to plot the cumulative dose over time for a selected detector
#TODO: Add the code to plot