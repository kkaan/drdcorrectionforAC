import matplotlib

matplotlib.use('Agg')  # Set the matplotlib backend to 'Agg'
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.animation import FuncAnimation
from matplotlib.colors import ListedColormap, BoundaryNorm

def create_animation(detector_arrays, xn, yn, detector_number):
    """
    Create an animation of the dose rate over time in the SNC Patient detector array display arrangement.

    Parameters:
    detector_arrays (list of np.array): List of 2D arrays representing the dose rate at each time point.

    Returns:
    None
    """
    def update(frame):
        ax.clear()  # Clear the current axes
        mask = detector_arrays[frame] == 0
        sns.heatmap(detector_arrays[frame], cmap=cmap, norm=norm, cbar=False, mask=mask, square=True, ax=ax,
                    xticklabels=50, yticklabels=50)
        ax.set_xticks(xticks)
        ax.set_yticks(yticks)
        ax.set_xticklabels(xticklabels)
        ax.set_yticklabels(yticklabels)
        ax.set_xlabel('X (cm)')
        ax.set_ylabel('Y (cm)')
        ax.set_title(f'Time: {frame * 50} ms')

    plt.ioff()  # Turn off interactive mode

    # Prepare the custom colormap
    colors = ["darkblue", "blue", "cyan", "green", "yellow"]  # Define the colors for the colormap
    cmap = ListedColormap(colors)

    # Prepare the custom norm
    boundaries = [0, 50, 100, 150, 300, np.inf]  # Define the boundaries for the colors
    norm = BoundaryNorm(boundaries, cmap.N, clip=True)

    # Set up the figure and axis for the animation
    fig, ax = plt.subplots(figsize=(20, 10))

    # Customizing the tick labels to fit the spatial dimensions
    xticks = np.linspace(0, detector_arrays[0].shape[1], num=11)
    yticks = np.linspace(0, detector_arrays[0].shape[0], num=5)
    xticklabels = [f"{x - 32.5}" for x in np.linspace(0, 65, num=11)]
    yticklabels = [f"{10 - x * 10}" for x in np.linspace(0, 2, num=5)]

    # Create the animation
    anim = FuncAnimation(fig, update, frames=len(detector_arrays), interval=50)

    # Save the animation
    anim.save(f'diff_dose_animation_selected_{xn}x{yn}_detector_{detector_number}.gif', dpi=80, writer='imagemagick')

    plt.close()  # Close the plot to prevent it from displaying statically

# def create_animation(detector_arrays):
#     """
#     Create an animation of the dose rate over time in the SNC Patient detector array display arrangement.
#
#     Parameters:
#     detector_arrays (list of np.array): List of 2D arrays representing the dose rate at each time point.
#
#     Returns:
#     None
#     """
#
#     def update(frame):
#         ax.clear()  # Clear the current axes
#         # Set 0 values to background colour
#         mask = detector_arrays[frame] == 0
#
#         sns.heatmap(detector_arrays[frame], cmap=cmap, vmax=200, cbar=False, mask=mask, square=True, ax=ax,
#                     xticklabels=50, yticklabels=50)
#         # Set the ticks and labels for each frame
#         ax.set_xticks(xticks)
#         ax.set_yticks(yticks)
#         ax.set_xticklabels(xticklabels)
#         ax.set_yticklabels(yticklabels)
#         ax.set_xlabel('X (cm)')
#         ax.set_ylabel('Y (cm)')
#         ax.set_title(f'Time: {frame * 50} ms')
#
#     plt.ioff()  # Turn off interactive mode
#
#     # Prepare the custom colormap
#     colors = ["blue", "cyan", "yellow", (0, 1, 0)]  # End with bright green
#     cmap = LinearSegmentedColormap.from_list("custom_green", colors)
#
#     # Set up the figure and axis for the animation
#     fig, ax = plt.subplots(figsize=(20, 10))
#
#     # Customizing the tick labels to fit the spatial dimensions
#     xticks = np.linspace(0, detector_arrays[0].shape[1], num=11)
#     yticks = np.linspace(0, detector_arrays[0].shape[0], num=5)
#     xticklabels = [f"{x - 32.5}" for x in np.linspace(0, 65, num=11)]
#     yticklabels = [f"{10 - x * 10}" for x in np.linspace(0, 2, num=5)]
#
#     # Create the animation
#     anim = FuncAnimation(fig, update, frames=len(detector_arrays), interval=50)
#
#     # Save the animation
#     anim.save('diff_dose_animation.gif', dpi=80, writer='imagemagick')
#
#     plt.close()  # Close the plot to prevent it from displaying statically


def create_cumulative_dose_animation(dose_rate_df, dose_accumulated_df, detector_index, start_frame, end_frame):
    """
    Create an animation of the accumulated dose over time for a specific detector,
    with the color of the marker indicating the dose rate.

    Parameters:
    dose_rate_df (pd.DataFrame): DataFrame containing the dose rate values.
    dose_accumulated_df (pd.DataFrame): DataFrame containing the dose values.
    detector_index (int): The index of the detector to plot.
    start_frame (int): The starting frame for the animation.
    end_frame (int): The ending frame for the animation.

    Returns:
    None
    """
    # Select the data for the specific detector
    dose_rate_detector = dose_rate_df.iloc[:, detector_index]
    dose_detector = dose_accumulated_df.iloc[:, detector_index]

    # Create a custom colormap based on the dose rate values
    colors = ["darkblue", "blue", "lightblue", "green"]
    bins = [50, 100, 150, np.inf]  # Dose rate thresholds for the colors
    colormap = ListedColormap(colors)

    # Calculate the maximum values for the x and y axes
    x_max = dose_detector.index.max()
    y_max = dose_detector.max()

    # Set up the figure and axis for the animation
    fig, ax = plt.subplots()

    # Set the limits of the x and y axes
    ax.set_xlim(0, x_max)
    ax.set_ylim(0, y_max)

    ax.set_title('Accumulated Dose Over Time (cGy)')
    ax.set_xlabel('Time')
    ax.set_ylabel('Accumulated Dose')

    def update(frame):
        # Calculate the color for the current frame based on the dose rate
        color_index = np.digitize(dose_rate_detector.iloc[frame], bins) - 1
        color = colormap.colors[color_index]

        # Plot the accumulated dose up to the current frame with the calculated color
        ax.scatter(dose_detector.index[:frame + 1], dose_detector.iloc[:frame + 1], color=color)

    # Create the animation
    anim = FuncAnimation(fig, update, frames=range(start_frame, end_frame + 1))

    # Save the animation
    anim.save(f'detector_{detector_index}_accumulated_dose_animation.gif', dpi=80, writer='imagemagick')

# def create_histogram(dose_rate_df, dose_accumulated_df):
#     # Calculate the sum and max of values at intervals of 300
#     def histogram_dose_rate(detector_values):
#         """
#         Calculate the sum of values at intervals of 300 for the selected detector.
#
#         Returns:
#         interval_sums (list): The sum of values for each interval.
#         interval_bins (list): The maximum value of each interval.
#         """
#         # Calculate the maximum value in the detector values
#         max_value = max(detector_values)
#         interval_sums = []
#         interval_bins = []
#         for i in range(0, int(max_value), 30):
#             interval_values = [value for value in detector_values if i <= value < i + 300]
#             interval_sum = sum(interval_values)
#             interval_bin = i if interval_values else 0  # Use 0 as the max if the interval is empty
#             interval_sums.append(interval_sum)
#             interval_bins.append(interval_bin)
#
#         return interval_sums, interval_bins
#
#     # Convert interval_max_values to string for use as category labels
#     accumulated_dose_for_interval_bin, interval_bins = histogram_dose_rate(detector_values)
#     interval_bins = [str(value) for value in interval_bins]
#
#     # Create the bar plot
#     sns.barplot(x=interval_bins, y=accumulated_dose_for_interval_bin)
#
#     # Set the title and labels
#     plt.title('Sum of Interval Values for Each Max Value')
#     plt.xlabel('Max Value of Interval')
#     plt.ylabel('Sum of Interval Values')
#
#     # Display the plot
#     plt.show()
