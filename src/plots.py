import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.animation import FuncAnimation
from matplotlib.colors import ListedColormap, BoundaryNorm
import pandas as pd

def create_animation(detector_arrays, xn, yn, detector_number):
    """
    Create an animation of the dose rate over time in the SNC Patient detector array display arrangement.

    Parameters:
    detector_arrays (ndarray): A 3D numpy array representing the dose rate at each time point.

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
    colors = ["dodgerblue", "deepskyblue", "turquoise", "springgreen", "seagreen"]  # Define the colors for the colormap
    cmap = ListedColormap(colors)

    # Prepare the custom norm
    boundaries = [0, 50, 100, 150, 300, np.inf]  # Define the boundaries for the colors
    norm = BoundaryNorm(boundaries, cmap.N, clip=True)

    # Set up the figure and axis for the animation
    fig, ax = plt.subplots(figsize=(20, 10))

    # Customizing the tick labels to fit the spatial dimensions
    xticks = np.linspace(0, detector_arrays.shape[2], num=11)
    yticks = np.linspace(0, detector_arrays.shape[1], num=5)
    xticklabels = [f"{x - 32.5}" for x in np.linspace(0, 65, num=11)]
    yticklabels = [f"{10 - x * 10}" for x in np.linspace(0, 2, num=5)]

    # Create the animation
    anim = FuncAnimation(fig, update, frames=detector_arrays.shape[0], interval=50)

    # Save the animation
    anim.save(f'diff_dose_animation_selected_{xn}x{yn}_detector_{detector_number}.gif', dpi=80, writer='imagemagick')

    plt.close()  # Close the plot to prevent it from displaying statically

def bar_doserate_histogram(dose_df, dose_rate_df, detector_names):
    all_data = []
    boundaries = [0, 50, 100, 150, 300, np.inf]
    labels = ['0-50', '50-100', '100-150', '150-300', '>300']

    for detector_name in detector_names:
        dose_detector = dose_df.iloc[:, detector_name]
        dose_rate_detector = dose_rate_df.iloc[:, detector_name]

        # Create a new column for the dose rate bins
        dose_rate_bins = pd.cut(dose_rate_detector, bins=boundaries, labels=labels, include_lowest=True)

        # Create a new DataFrame with the dose, dose rate bins, and detector index
        df = pd.DataFrame({
            'Dose': dose_detector,
            'Dose Rate Interval': dose_rate_bins,
            'Detector Names': detector_name  # Change 'Detector' to 'Detector Names'
        })
        all_data.append(df)

    all_data_df = pd.concat(all_data)

    # Group the data by 'Detector Names' and 'Dose Rate Interval' and calculate the sum of 'Dose' for each group
    grouped_data = all_data_df.groupby(['Detector Names', 'Dose Rate Interval'])['Dose'].sum().reset_index()

    # Define your colors
    colors = ["dodgerblue", "deepskyblue", "turquoise", "springgreen", "seagreen"]  # Use the blue-green spectrum colors

    # Create the bar plot
    bar_plot = sns.barplot(
        data=grouped_data,
        x='Detector Names',
        y='Dose',
        hue='Dose Rate Interval',
        palette=colors,  # Use the list of colors directly
        edgecolor=".3",
        linewidth=.5,
    )
    bar_plot.set_ylim(0, 20)  # Adjust these values as needed

    plt.xlabel('Detector Names')  # Set x-axis label to 'Detector Names'
    plt.ylabel('Dose Sum')  # Set y-axis label to 'Dose Sum'
    plt.savefig('stacked_histogram.png')
    plt.show()

def scatter_cumulative_dose(dose_rate_df, dose_accumulated_df, detector_name):
    """
    Create a seaborn scatter plot with dose accumulated in the y-axis and time in the x-axis.
    The hue of the markers will be determined by the dose rate intervals.

    Parameters:
    dose_rate_df (pd.DataFrame): DataFrame containing the dose rate values.
    dose_accumulated_df (pd.DataFrame): DataFrame containing the dose values.
    detector_name (int): The index of the detector to plot.

    Returns:
    None
    """

    try:
        # Select the data for the specific detector
        dose_rate_detector = dose_rate_df.iloc[:, detector_name]
        dose_detector = dose_accumulated_df.iloc[:, detector_name]
    except IndexError:
        print("Error: Detector index out of range.")
        return

    # Calculate time assuming each row increment represents 50 ms
    time = dose_rate_df.index * 50

    # Create a new DataFrame combining the data
    data = pd.DataFrame({
        'Time': time,
        'Dose Accumulated': dose_detector.values,
        'Dose Rate': dose_rate_detector.values
    })

    # Create a new column for the dose rate intervals
    bins = [0, 50, 100, 150, 300, np.inf]
    color_labels = ['0-50', '50-100', '100-150', '150-300', '>300']
    colors = ["dodgerblue", "deepskyblue", "turquoise", "springgreen", "seagreen"]
    data['Dose Rate Interval'] = pd.cut(data['Dose Rate'], bins=bins, include_lowest=True, labels=color_labels)

    # Set up the figure and axis
    fig, ax = plt.subplots()

    # Plot using seaborn
    sns.scatterplot(data=data,
                    x='Time',
                    y='Dose Accumulated',
                    hue='Dose Rate Interval',
                    palette=colors,
                    ax=ax)

    ax.set_title('Accumulated Dose Over Time (cGy)')
    ax.set_xlabel('Time (ms)')
    ax.set_ylabel('Accumulated Dose (cGy)')
    ax.grid(True)
    ax.legend(loc='best')

    plt.savefig('cumulative_dose.png')
    plt.close()  # Closes the plot to avoid displaying it in interactive environments

