import numpy as np

def get_intrinsic_corrections(array_data):
    """
    Calculate the Intrinsic Correction array as an element-wise division of Corrected Counts by Raw Counts,
    including preserving the positional data in the first two columns and the last three rows, and ensuring the
    first row retains its original values from Corrected Counts. The very last row, consisting solely of None
    values, is left unchanged to match other arrays' structures.

    Parameters:
    array_data (dict): A dictionary containing numpy arrays including 'Corrected Counts' and 'Raw Counts'.

    Returns:
    numpy.ndarray: An array of intrinsic corrections, including positional data, or None if an error occurs.
    """
    try:
        corrected_counts = array_data.get('Corrected Counts')
        raw_counts = array_data.get('Raw Counts')

        if corrected_counts is None or raw_counts is None:
            raise ValueError("Missing data: 'Corrected Counts' and/or 'Raw Counts' arrays are not available.")

        if corrected_counts.shape != raw_counts.shape:
            raise ValueError("Shape mismatch: 'Corrected Counts' and 'Raw Counts' arrays must have the same dimensions.")

        # Exclude the first two columns and last three rows which contain non-numeric positional data
        numeric_corrected = corrected_counts[1:-3, 2:]  # Start from second row for numeric processing
        numeric_raw = raw_counts[1:-3, 2:]  # Apply same row exclusion as numeric_corrected

        # Ensure arrays are in float format for processing
        numeric_corrected = np.array(numeric_corrected, dtype=float)
        numeric_raw = np.array(numeric_raw, dtype=float)

        # Perform elementwise division, handling division by zero safely
        with np.errstate(divide='ignore', invalid='ignore'):
            intrinsic_correction = np.divide(numeric_corrected, numeric_raw)
            intrinsic_correction = np.nan_to_num(intrinsic_correction)  # Convert NaNs to zero if any divisions by zero occurred

        # Create a full array to hold both numeric and non-numeric data
        full_correction = np.full_like(corrected_counts, None, dtype=object)
        full_correction[1:-3, 2:] = intrinsic_correction  # Adjust indices to match the shape
        full_correction[:, :2] = corrected_counts[:, :2]  # Retain the first two columns as-is
        full_correction[-3:, :] = corrected_counts[-3:, :]  # Retain the last three rows as-is

        return full_correction

    except ValueError as e:
        print(f"Value Error: {e}")
        return None
    except TypeError as e:
        print(f"Type Error: Please ensure all values are numeric: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def pulse_rate_correction(counts_acummulated_df, jager_pr_coefficients):
    """
    Corrects the count values in the dataframe using the Jager pulse rate correction coefficients.

    Parameters:
    counts_accumulated_df (DataFrame): A pandas DataFrame containing the accumulated count values.
    jager_pr_coefficients (ndarray): An array containing the Jager pulse rate correction coefficients.

    Returns:
    jcf_pr_df (DataFrame): A pandas DataFrame containing the Jager correction factor values.
    """
    a, b, c = jager_pr_coefficients

    # Calculate the count rate
    count_df = counts_acummulated_df.diff()  # cGy
    count_df = count_df[1:]  # The first row will be NaN, drop the first row

    # Apply the correction factor formula
    jcf_pr_df = c - a * np.exp(-b * count_df)
    pr_corrected_count_df = count_df * jcf_pr_df
    return pr_corrected_count_df

def dose_per_pulse_correction(counts_acummulated_df, jager_dpp_coefficients):
    """
    Corrects the count values in the dataframe using the Jager dose per pulse correction coefficients.

    Parameters:
    counts_df (DataFrame): A pandas DataFrame containing the accumulated count values.
    jager_dpp_coefficients (ndarray): An array containing the Jager dose per pulse correction coefficients.

    Returns:
    jcf_dpp_df (DataFrame): A pandas DataFrame containing the Jager correction factor values.
    """
    a, b, c = jager_dpp_coefficients

    # Calculate the count rate
    count_df = counts_acummulated_df.diff()  # cGy
    count_df = count_df[1:]  # The first row will be NaN, drop the first row

    # Apply the correction factor formula
    jcf_dpp_df = c - a * np.exp(-b * count_df)
    dpp_corrected_count_df = count_df * jcf_dpp_df
    return dpp_corrected_count_df
