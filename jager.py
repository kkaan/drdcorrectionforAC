import pandas as pd
import numpy as np

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




