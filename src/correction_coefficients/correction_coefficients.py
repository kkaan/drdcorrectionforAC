"""
This module, `correction_coefficients.py`, contains functions for calculating and visualizing correction coefficients for dose rate dependency in ArcCheck measurements.

The module includes the following functions:

- `get_pr_data_from_acm_files`: Extracts the average counts/50ms from ACM files in a specified directory.
- `saturation_fit`: Defines an exponential fitting function for curve fitting.
- `get_correction_coefficients`: Calculates the correction coefficients based on the average counts/50ms and relative signal values.
- `plot_correction_curve`: Plots the correction curve with the data points and the fitted exponential function.
- `plot_counts_per_50ms`: Plots the counts per 50ms at different nominal dose rates.
- `main`: Main function to execute the correction coefficient calculations and plotting.

This module is part of a larger project aimed at analyzing and correcting dose rate dependencies in ArcCheck measurements.

"""

import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.optimize import curve_fit
import datetime



# Add the src directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src import io_snc


def get_pr_data_from_acm_files(pr_measurement_folder):
    """
    Get the average counts/50ms from the ACM files.

    Parameters
    ----------
    pr_measurement_folder : str
        Path to the folder containing ACM files.

    Returns
    -------
    list of tuple
        List of tuples containing the file name and the average counts/50ms for each nominal dose rate.
    """
    diode_numbers = np.array([758, 759, 760, 761, 692, 693, 694, 695, 626, 627, 628, 629]).astype(str)

    # initialize a dictionary to store the average counts/50ms  for each file over all
    # diodes in the middle 200 frames.
    counts_per_50ms_dict = {}

    # initialize a list to store the average counts per 50ms for each file
    counts_per_50ms_list = []

    for acm_file in os.listdir(pr_measurement_folder):
        acm_file_path = os.path.join(pr_measurement_folder, acm_file)
        frame_data_df, diode_data_df, bkrnd_and_calibration_df = io_snc.parse_acm_file(acm_file_path)

        # Grab the count rate from the middle 100 frames of the measurement
        num_frames = len(diode_data_df)
        start_frame = num_frames // 2 - 50
        end_frame = start_frame + 100
        middle_frames = diode_data_df.iloc[start_frame:end_frame]

        # Calculate the count rate by differencing the accumulated counts
        diode_data_diff_df = middle_frames.diff().iloc[1:]

        # Extract the count rate for the specified diodes in the middle frames
        count_rate_df = diode_data_diff_df.loc[:, diode_numbers]

        # Calculate the average count rate for each frame across the selected diodes
        avg_count_rate_per_frame = count_rate_df.mean(axis=1)
        avg_count_rate_per_frame = avg_count_rate_per_frame.values
        counts_per_50ms_dict[acm_file] = avg_count_rate_per_frame

        # Calculate the average count rate for the selected diodes
        avg_count_rate = count_rate_df.mean().mean()
        counts_per_50ms_list.append((acm_file, avg_count_rate))

    # Convert the dictionary to a DataFrame
    counts_per_50ms_df = pd.DataFrame.from_dict(counts_per_50ms_dict, orient='index')
    # Save the DataFrame to a CSV file
    counts_per_50ms_df.to_csv('counts_per_50ms.csv')

    counts_per_50ms_list = sorted(counts_per_50ms_list, key=lambda x: x[1])
    return counts_per_50ms_list


def saturation_func(x, a, b, c):
    """
    Exponential fitting function.

    Parameters
    ----------
    x : array_like
        Independent variable data.
    a : float
        Coefficient for the exponential function.
    b : float
        Exponential rate.
    c : float
        Offset value.

    Returns
    -------
    array_like
        The calculated dependent variable values.
    """
    return c - a * np.exp(-b * x)


def get_correction_coefficients(counts_per_50ms, relative_signal):
    """
    Calculate the correction coefficients for the dose rate dependency.

    Parameters
    ----------
    counts_per_50ms : list of tuple
        List of tuples containing the file name and the average counts/50ms for each nominal dose rate.
    relative_signal : array_like
        Array of relative signal values corresponding to the nominal dose rates.

    Returns
    -------
    tuple of float
        The fitted coefficients (a, b, c) for the exponential correction function.
    """
    counts_per_50ms = np.array([data[1] for data in counts_per_50ms])
    initial_guess = [0.035, 5.21e-5, 1.0]
    # noinspection PyTupleAssignmentBalance
    params, covariance = curve_fit(saturation_func, counts_per_50ms,
                                   relative_signal, p0=initial_guess)
    a_fit, b_fit, c_fit = params

    return a_fit, b_fit, c_fit, covariance

def get_coefficient_file_path(date=None):
    """
    Get the path to the file where the correction coefficients will be written.

    Returns
    -------
    str
        The file path for the correction coefficients.
    """
    # get user input on type of whether it DPP or PR
    coefficient_file_directory = input("Enter the directory to the file where the correction coefficients will be written: ")

    # Get the DRD type, ArcCheck SN from the user
    DRD_type = input("Enter the DRD type: ")
    ArcCheck_SN = input("Enter the ArcCheck SN: ")

    # Get today's date
    today = datetime.date.today()
    date = today.strftime("%Y-%m-%d")

    # construct coefficient file name from DRD type, ArcCheck SN and Date
    coefficient_file_name = f"{DRD_type}_{ArcCheck_SN}_{date}.txt"

    # construct the full path to the coefficient file
    coefficient_file_path = os.path.join(coefficient_file_directory, coefficient_file_name)

    return coefficient_file_path

def write_correction_coefficients_to_file(coefficient_file_path, a_fit, b_fit, c_fit, covariance):
    with open(coefficient_file_path, 'w') as f:
        # Write the variable names and their values to the file
        f.write(f"a_fit = {a_fit}\n")
        f.write(f"b_fit = {b_fit}\n")
        f.write(f"c_fit = {c_fit}\n")
        f.write(f"covariance = {covariance}\n")


def plot_correction_curve(counts_per_50ms, relative_signal, a_fit, b_fit, c_fit):
    """
    Plot the correction curve with the data points and the fitted exponential function.

    Parameters
    ----------
    counts_per_50ms : list of tuple
        List of tuples containing the file name and the average counts/50ms for each nominal dose rate.
    relative_signal : array_like
        Array of relative signal values corresponding to the nominal dose rates.
    a_fit : float
        Fitted coefficient for the exponential function.
    b_fit : float
        Fitted exponential rate.
    c_fit : float
        Fitted offset value.
    """
    counts_per_50ms = np.array([data[1] for data in counts_per_50ms])

    # Generate fitted curve data points
    x_fit = np.linspace(counts_per_50ms.min(), counts_per_50ms.max(), 500)
    y_fit = saturation_func(x_fit, a_fit, b_fit, c_fit)

    # Set Seaborn style
    sns.set(style="whitegrid")

    # Create a plot with Seaborn
    plt.figure(figsize=(10, 6))
    sns.lineplot(x=x_fit, y=y_fit, label=f'Exponential fit, a={a_fit:.4f}, b={b_fit:.2e}, c={c_fit:.3f}')
    sns.scatterplot(x=counts_per_50ms, y=relative_signal, label='Data points')

    #plt.ioff()  # Turn off interactive mode

    # Plot the data points and the fitted curve
    plt.figure(figsize=(8, 6))
    plt.plot(x_fit, y_fit, label=f'Exponential fit, a={a_fit:.4f}, b={b_fit:.2e}, c={c_fit:.3f}')
    plt.errorbar(counts_per_50ms, relative_signal, yerr=0.01, fmt='o',
                 label='Data points')  # Assuming 1% error for demonstration

    # Customize plot
    plt.xlabel('Counts/50ms')
    plt.ylabel('Relative signal')
    plt.title('Pulse rate (MU/min)')
    plt.legend()
    plt.grid(True)
    plt.show()
    plt.savefig('counts_per_50ms.png')


def plot_counts_per_50ms(counts_per_50ms):
    """
    Plot the counts per 50ms at different nominal dose rates.

    Parameters
    ----------
    counts_per_50ms : list of tuple
        List of tuples containing the file name and the average counts/50ms for each nominal dose rate.
    """
    counts_per_50ms = [data[1] for data in counts_per_50ms]

    # Set Seaborn style
    sns.set(style="whitegrid")
    #plt.ioff()  # Turn off interactive mode
    # Create a plot with Seaborn
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x=range(len(counts_per_50ms)), y=counts_per_50ms, label='Counts/50ms')

    # Customize plot
    plt.xlabel('Nominal dose rate')
    plt.ylabel('Counts/50ms')
    plt.title('Counts per 50ms at different nominal dose rates')
    plt.legend()
    plt.grid(True)
    plt.show()
    plt.savefig('counts_per_50ms_nominal.png')


def main():
    """
    Main function to execute the correction coefficient calculations and plotting.
    """

    pr_measurement_folder = r"P:\02_QA Equipment\02_ArcCheck\05_Commissoning\03_NROAC\Dose Rate Dependence Fix\NRO PR Coefficient"
    counts_per_50ms = get_pr_data_from_acm_files(pr_measurement_folder)
    # plot_counts_per_50ms(counts_per_50ms)
    relative_signal = np.array([0.964, 0.971, 0.980, 0.988, 0.994, 0.995, 1.000, 1.000])
    a_fit, b_fit, c_fit, covariance = get_correction_coefficients(counts_per_50ms, relative_signal)
    coefficient_file_path = get_coefficient_file_path()
    write_correction_coefficients_to_file(coefficient_file_path, a_fit, b_fit, c_fit, covariance)
    # plot_correction_curve(counts_per_50ms, relative_signal, a_fit, b_fit, c_fit)


if __name__ == "__main__":
    main()
