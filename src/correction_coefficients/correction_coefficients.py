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

       Parameters:
       pr_measurement_folder (str): Path to the folder containing ACM files.

       Returns:
       list: List of tuples containing the file name and the average counts/50ms for each nominal dose rate.
       """
    # Convert diode numbers to strings
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

def get_correction_coefficients(counts_per_50ms, relative_signal):
    counts_per_50ms = [data[1] for data in counts_per_50ms]
    # Define the model function based on the given equation
    def model_func(x, a, b, c):
        return c - a * np.exp(-b * x)

    # Fit the model to the data
    initial_guess = [0.035, 5.21e-5, 1.0]  # Initial guesses for a, b, and c
    params, covariance = curve_fit(model_func, counts_per_50ms, relative_signal, p0=initial_guess)

    # Extract the fitted parameters
    a_fit, b_fit, c_fit = params
    return a_fit, b_fit, c_fit
def plot_correction_curve(counts_per_50ms, relative_signal, a_fit, b_fit, c_fit):
    def model_func(x, a, b, c):
        return c - a * np.exp(-b * x)

    # Extract only the numerical data from the tuples
    counts_per_50ms = [data[1] for data in counts_per_50ms]

    # # #Directly use saved values from the debugging session
    # a_fit = 0.029895257663822866
    # b_fit = 4.072015230665901e-05
    # c_fit = 1.0011070715447767
    # counts_per_50ms = [2317.7558333333336,
    #                    4733.205000000001,
    #                    9608.688333333334,
    #                    19436.3675,
    #                    39283.20500000001,
    #                    39299.387500000004,
    #                    80095.79083333332,
    #                    80268.56916666665]
    # relative_signal = [0.964,
    #                    0.971,
    #                    0.980,
    #                    0.988,
    #                    0.994,
    #                    0.995,
    #                    1.000,
    #                    1.000]


    # Generate x values for plotting the fitted curve
    x_fit = np.linspace(0, max(counts_per_50ms), 1000)
    y_fit = model_func(x_fit, a_fit, b_fit, c_fit)

    # Set Seaborn style
    sns.set(style="whitegrid")

    # Create a plot with Seaborn
    plt.figure(figsize=(10, 6))
    sns.lineplot(x=x_fit, y=y_fit, label=f'Exponential fit, a={a_fit:.4f}, b={b_fit:.2e}, c={c_fit:.3f}')
    sns.scatterplot(x=counts_per_50ms, y=relative_signal, label='Data points')

    plt.ioff() # Turn off interactive mode

    # Plot the data points and the fitted curve
    plt.figure(figsize=(8, 6))
    plt.plot(x_fit, y_fit, label=f'Exponential fit, a={a_fit:.4f}, b={b_fit:.2e}, c={c_fit:.3f}')
    plt.errorbar(counts_per_50ms, relative_signal, yerr=0.01, fmt='o', label='Data points')  # Assuming 1% error for demonstration

    # Customize plot
    plt.xlabel('Counts/50ms')
    plt.ylabel('Relative signal')
    plt.title('Pulse rate (MU/min)')
    plt.legend()
    plt.grid(True)

    plt.show()

def plot_counts_per_50ms(counts_per_50ms):
    # Extract only the numerical data from the tuples
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
    pr_measurement_folder = r"P:\02_QA Equipment\02_ArcCheck\05_Commissoning\03_NROAC\Dose Rate Dependence Fix\NRO PR Coefficient"
    counts_per_50ms = get_pr_data_from_acm_files(pr_measurement_folder)
    plot_counts_per_50ms(counts_per_50ms)
    relative_signal = np.array([0.964, 0.971, 0.980, 0.988, 0.994, 0.995, 1.000, 1.000])
    a_fit, b_fit, c_fit = get_correction_coefficients(counts_per_50ms, relative_signal)
    plot_correction_curve(counts_per_50ms, relative_signal, a_fit, b_fit, c_fit)

if __name__ == "__main__":
    main()
