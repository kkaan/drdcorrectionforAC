import os
import numpy as np
import io_snc
import plots
from corrections import apply_jager_corrections, get_intrinsic_corrections

def apply_corrections(counts_accumulated_df, bkrnd_and_calibration_df, include_intrinsic_corrections, array_data):
    """
    Apply corrections based on user input.

    Parameters:
    counts_accumulated_df (DataFrame): DataFrame with accumulated counts.
    bkrnd_and_calibration_df (DataFrame): DataFrame with background and calibration data.
    include_intrinsic_corrections (str): Whether to include intrinsic corrections ('y' or 'n').
    array_data (ndarray): Array data.

    Returns:
    ndarray: Corrected count array.
    """
    if include_intrinsic_corrections == 'y':
        intrinsic_corrections = get_intrinsic_corrections(array_data)
    else:
        intrinsic_corrections = None

    corrected_count_array = apply_jager_corrections(counts_accumulated_df, bkrnd_and_calibration_df, intrinsic_corrections)

    return corrected_count_array

def read_files(acml_path, txt_path):
    """
    Read and parse ACM and TXT files.

    Parameters:
    acml_path (str): Path to the ACM file.
    txt_path (str): Path to the TXT file.

    Returns:
    tuple: DataFrames and arrays with parsed data.
    """
    frame_data_df, counts_accumulated_df, bkrnd_and_calibration_df = io_snc.parse_acm_file(acml_path)
    header_data = io_snc.parse_arccheck_header(txt_path)
    array_data = io_snc.parse_arrays_from_file(txt_path)
    return frame_data_df, counts_accumulated_df, bkrnd_and_calibration_df, header_data, array_data


def generate_plots(dose_rate_arrays, dose_df, dose_rate_df, dose_accumulated_df, startframe, endframe, detector_number):
    """
    Generate plots and animations.

    Parameters:
    dose_rate_arrays (ndarray): Dose rate arrays.
    dose_df (DataFrame): DataFrame with dose data.
    dose_rate_df (DataFrame): DataFrame with dose rate data.
    dose_accumulated_df (DataFrame): DataFrame with accumulated dose data.
    startframe (int): Starting frame.
    endframe (int): Ending frame.
    detector_number (int): Detector number.
    """
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
    """
    Calculate dose values and dose rate values.

    Parameters:
    counts_accumulated_df (DataFrame): DataFrame with accumulated counts.
    dose_per_count (float): Dose per count.

    Returns:
    tuple: DataFrames with dose values and dose rate values.

    """

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

def get_user_input():
    """Get user input for batch folder path and correction type."""
    default_path = (r'P:\02_QA Equipment\02_ArcCheck\05_Commissoning\03_NROAC\Dose Rate Dependence Fix\Test on '
                    r'script\BatchrunMeasured')
    batch_folder_path = input(
        f"Enter the path to the folder containing the acm files (Press enter to use default path {default_path}): ")
    if batch_folder_path == '':
        batch_folder_path = default_path

    correction_type = input("Enter the type of correction to apply (dpp or pr): ")
    include_intrinsic_corrections = input("Do you want to re-apply intrinsic corrections? (y/n): ")

    return batch_folder_path, correction_type, include_intrinsic_corrections


def main():
    batch_folder_path, correction_type, include_intrinsic_corrections = get_user_input()

    for file in os.listdir(batch_folder_path):
        if file.endswith(".acm"):
            print(f"Processing file: {file}")
            acm_file_path = os.path.join(batch_folder_path, file)
            txt_file_path = os.path.join(batch_folder_path, file[:-4] + ".txt")

            if not os.path.isfile(txt_file_path):
                print(f"Matching .txt file for {file} not found. Skipping this file.")
                continue

            try:
                (frame_data_df,
                 counts_accumulated_df,
                 bkrnd_and_calibration_df,
                 header_data,
                 array_data) = read_files(acm_file_path, txt_file_path)

                if include_intrinsic_corrections == 'y':
                    file_name_suffix_intrinsic = '_intrinsic'
                else:
                    file_name_suffix_intrinsic = ''

                corrected_count_array = apply_corrections(counts_accumulated_df,
                                                          bkrnd_and_calibration_df,
                                                          include_intrinsic_corrections,
                                                          array_data)

                array_data_to_write = array_data.copy()

                if correction_type == 'pr':
                    array_data_to_write['Corrected Counts'] = snc_format_array(corrected_count_array[0],
                                                                               array_data_to_write['Corrected Counts'])
                else:
                    array_data_to_write['Corrected Counts'] = snc_format_array(corrected_count_array[1],
                                                                               array_data_to_write['Corrected Counts'])

                write_file_path = (txt_file_path[:-4] + '_corrected_' + correction_type +
                                   file_name_suffix_intrinsic + '.txt')

                io_snc.write_snc_txt_file(array_data_to_write, header_data, write_file_path)

            except FileNotFoundError:
                print(f"File {file} not found.")
            except Exception as e:
                print(f"An error occurred while processing {file}: {str(e)}")

if __name__ == "__main__":
    main()

