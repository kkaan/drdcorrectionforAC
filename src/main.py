import numpy as np
import io_snc
import plots
import corrections
import pandas as pd

# Configuration
acml_file_path = r'P:\02_QA Equipment\02_ArcCheck\05_Commissoning\03_NROAC\Dose Rate Dependence Fix\Test on script\13-Jun-2023-Plan7 6X.acm'
txt_file_path = r'P:\02_QA Equipment\02_ArcCheck\05_Commissoning\03_NROAC\Dose Rate Dependence Fix\Test on script\13-Jun-2023-Plan7 6X.txt'

# TODO: Get dose per count calibration factor from acl file directly.
dose_per_count: float = 7.7597E-06  # cGy/count


def read_files(acml_path, txt_path):
    frame_data_df, counts_accumulated_df, bkrnd_and_calibration_df = io_snc.parse_acm_file(acml_path)
    header_data = io_snc.parse_arccheck_header(txt_path)
    array_data = io_snc.parse_arrays_from_file(txt_path)
    return frame_data_df, counts_accumulated_df, bkrnd_and_calibration_df, header_data, array_data

def apply_jager_corrections(counts_accumulated_df, bkrnd_and_calibration_df, intrinsic_corrections=None):
    """Apply Jager pulse rate and dose per pulse corrections."""
    a_pr, b_pr, c_pr = 0.035, 5.21 * 10 ** -5, 1
    jager_pr_coefficients = np.array([a_pr, b_pr, c_pr])

    a_dpp, b_dpp, c_dpp = 0.0978, 3.33 * 10 ** -5, 1.011
    jager_dpp_coefficients = np.array([a_dpp, b_dpp, c_dpp])

    pr_corrected_count_sum = corrections.pulse_rate_correction(counts_accumulated_df, bkrnd_and_calibration_df,
                                                               jager_pr_coefficients)
    dpp_corrected_count_sum = corrections.dose_per_pulse_correction(counts_accumulated_df, bkrnd_and_calibration_df,
                                                                    jager_dpp_coefficients)

    # Create a new DataFrame
    corrected_count = pd.DataFrame({
        'pr_corrected_dose_df': pr_corrected_count_sum,
        'dpp_corrected_dose_df': dpp_corrected_count_sum
    })

    # In the format of the SNC txt file
    corrected_count_array = io_snc.detector_arrays(corrected_count.T)

    # Apply intrinsic corrections if provided
    if intrinsic_corrections is not None:
        numeric_intrinsic = intrinsic_corrections[1:-3, 2:]
        numeric_intrinsic = np.array(numeric_intrinsic, dtype=float)
        corrected_count_array *= numeric_intrinsic

    return corrected_count_array


def generate_plots(dose_rate_arrays, dose_df, dose_rate_df, dose_accumulated_df, startframe, endframe, detector_number):
    """Generate plots and animations."""

    xn, yn = 31, 15
    diode_numbers_in_snc_array = io_snc.diode_numbers_in_snc_array()
    X = np.arange(-32.5, 33, 0.5)
    Y = np.arange(10, -10.5, -0.5)

    row, col = np.where(diode_numbers_in_snc_array == detector_number)
    row, col = row[0], col[0]

    half_xn = xn // 2
    half_yn = yn // 2

    start_row = row - half_yn if row - half_yn >= 0 else row
    end_row = row + half_yn + 1 if row + half_yn + 1 <= diode_numbers_in_snc_array.shape[0] else row + 1
    start_col = col - half_xn if col - half_xn >= 0 else col
    end_col = col + half_xn + 1 if col + half_xn + 1 <= diode_numbers_in_snc_array.shape[1] else col + 1

    selected_dose_rate_arrays = dose_rate_arrays[startframe:endframe, start_row:end_row, start_col:end_col]
    selected_X = X[start_col:end_col]
    selected_Y = Y[start_row:end_row]

    plots.create_animation(dose_rate_arrays, xn, yn, detector_number)
    plots.scatter_cumulative_dose(dose_rate_df[startframe:endframe], dose_accumulated_df[startframe:endframe],
                                  detector_number)
    plots.bar_doserate_histogram(dose_df, dose_rate_df, [630, 610, 590, 570, 550])


def calculate_dose_values(counts_accumulated_df, dose_per_count):
    # Calculate the dose values
    # Dose per count calibration factor

    # Calculate the dose values
    dose_accumulated_df = counts_accumulated_df * dose_per_count  # cGy

    # Calculate the difference between current row and previous row
    dose_df = dose_accumulated_df.diff()  # cGy
    dose_df = dose_df[1:]  # The first row will be NaN, drop the first row
    dose_accumulated_df = dose_accumulated_df[1:]  # Matching the length of dose_df

    # Calculate the dose rate values
    # Assuming the time interval between each frame is 50 ms
    time_interval = 50 / 60000  # in minutes
    dose_rate_df = dose_df / time_interval  # cGy/min

    # Create a ndarray of detector arrays arranged in the SNC Patient display configuration
    # Each array represents a frame of the detector array at a specific time point
    dose_rate_arrays = io_snc.detector_arrays(dose_rate_df)

    return dose_df, dose_accumulated_df, dose_rate_df, dose_rate_arrays


def snc_format_array(corrected_count_array, formatted_counts):
    """
    Formats the array to be compatible with the SNC measured txt file.

    Parameters:
    corrected_count_array (numpy.ndarray): The array containing corrected dose values.
    formatted_counts (numpy.ndarray): The array containing the counts with positional data directly from measured file.

    Returns:
    numpy.ndarray: Corrected values in format ready for insertion into SNC txt file.
    """
    # Convert corrected_array values to strings with 16 digits
    corrected_array_str = np.array([["{:.15f}".format(value) for value in row] for row in corrected_count_array])

    # Insert corrected_dose_array_str into new_dose_counts while preserving positional data
    formatted_counts[1:42, 2:133] = corrected_array_str

    return formatted_counts


def main():
    # Read the necessary files and parse the data
    (frame_data_df, counts_accumulated_df, bkrnd_and_calibration_df,
     header_data, array_data) = read_files(acml_file_path, txt_file_path)

    # Get the intrinsic corrections from the parsed array data
    # The intrinsic corrections represent the field size and angular correction applied by the SNC Patient software
    intrinsic_corrections = corrections.get_intrinsic_corrections(array_data)

    # Apply the Jager pulse rate and dose per pulse corrections to the accumulated counts
    corrected_count_array = apply_jager_corrections(counts_accumulated_df, bkrnd_and_calibration_df)

    # Make a copy of the original array data
    array_data_to_write = array_data.copy()

    # Format the corrected count array to be compatible with the SNC measured txt file
    # The corrected count array is inserted into the 'Corrected Counts' field of the copied array data
    array_data_to_write['Corrected Counts'] = snc_format_array(corrected_count_array[1],
                                                               array_data_to_write['Corrected Counts'])

    # Write the corrected array data to a new .txt file
    # The header data and the name of the new file ('corrected_file.txt') are also provided
    io_snc.write_snc_txt_file(array_data_to_write, header_data, 'corrected_file.txt')

    # # For plotting:
    # dose_df, dose_accumulated_df, dose_rate_df, dose_rate_arrays = calculate_dose_values(
    #     counts_accumulated_df, dose_per_count)
    #
    # generate_plots(dose_rate_arrays, dose_df, dose_rate_df, dose_accumulated_df,
    #                startframe=1550, endframe=1600,
    #                detector_number=610)


if __name__ == "__main__":
    main()

# TODO: Create a function to put the corrected dose values back into the .txt file
