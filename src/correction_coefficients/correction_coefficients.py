"""
This module, `correction_coefficients.py`, contains functions for calculating and visualizing correction coefficients for dose rate dependency in ArcCheck measurements.

The module includes the following functions:

- `get_pr_data_from_acm_files`: Extracts the average counts/50ms from ACM files in a specified directory.
- `exponential_fit`: Defines an exponential fitting function for curve fitting.
- `get_correction_coefficients`: Calculates the correction coefficients based on the average counts/50ms and relative signal values.
- `plot_correction_curve`: Plots the correction curve with the data points and the fitted exponential function.
- `plot_counts_per_50ms`: Plots the counts per 50ms at different nominal dose rates.
- `main`: Main function to execute the correction coefficient calculations and plotting.

This module is part of a larger project aimed at analyzing and correcting dose rate dependencies in ArcCheck measurements.

"""

import os
import sys

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.optimize import curve_fit

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
    counts_per_50ms_list = []

    for acm_file in os.listdir(pr_measurement_folder):
        acm_file_path = os.path.join(pr_measurement_folder, acm_file)
        frame_data_df, diode_data_df, bkrnd_and_calibration_df = io_snc.parse_acm_file(acm_file_path)

        # Ensure the frame data is sorted by time or frame number if necessary
        diode_data_df.sort_index(inplace=True)

        # Calculate the count rate by differencing the accumulated counts
        diode_data_diff = diode_data_df.diff().iloc[1:]

        # Grab the count rate from the middle 100 frames of the measurement
        num_frames = len(diode_data_diff)
        start_frame = num_frames // 2 - 50
        end_frame = start_frame + 100
        middle_frames = diode_data_diff.iloc[start_frame:end_frame]

        # Extract the count rate for the specified diodes in the middle frames
        count_rate_df = middle_frames.loc[:, diode_numbers]

        # Calculate the average count rate for the selected diodes
        avg_count_rate = count_rate_df.mean().mean()
        counts_per_50ms_list.append((acm_file, avg_count_rate))

    counts_per_50ms_list = sorted(counts_per_50ms_list, key=lambda x: x[1])
    return counts_per_50ms_list


def exponential_fit(x, a, b, c):
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
    return a * np.exp(b * x) + c


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

    # Perform the curve fitting
    popt, _ = curve_fit(exponential_fit, counts_per_50ms, relative_signal)
    return tuple(popt)


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
    y_fit = exponential_fit(x_fit, a_fit, b_fit, c_fit)

    # Set Seaborn style
    sns.set(style="whitegrid")

    # Create a plot with Seaborn
    plt.figure(figsize=(10, 6))
    sns.lineplot(x=x_fit, y=y_fit, label=f'Exponential fit, a={a_fit:.4f}, b={b_fit:.2e}, c={c_fit:.3f}')
    sns.scatterplot(x=counts_per_50ms, y=relative_signal, label='Data points')

    plt.ioff()  # Turn off interactive mode

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


def main():
    """
    Main function to execute the correction coefficient calculations and plotting.
    """
    pr_measurement_folder = r"P:\02_QA Equipment\02_ArcCheck\05_Commissoning\03_NROAC\Dose Rate Dependence Fix\NRO PR Coefficient"
    counts_per_50ms = get_pr_data_from_acm_files(pr_measurement_folder)
    plot_counts_per_50ms(counts_per_50ms)
    relative_signal = np.array([0.964, 0.971, 0.980, 0.988, 0.994, 0.995, 1.000, 1.000])
    a_fit, b_fit, c_fit = get_correction_coefficients(counts_per_50ms, relative_signal)
    plot_correction_curve(counts_per_50ms, relative_signal, a_fit, b_fit, c_fit)


if __name__ == "__main__":
    main()
