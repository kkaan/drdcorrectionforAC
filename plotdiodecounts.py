import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.animation import FuncAnimation
from matplotlib.colors import LinearSegmentedColormap


# Function to update each frame in the animation
def update(frame):
    ax.clear()  # Clear the current axes
    # Set 0 values to background colour
    mask = diff_dose_arrays[frame] == 0

    sns.heatmap(diff_dose_arrays[frame], cmap=cmap, vmax=200, cbar=False, mask=mask, square=True, ax=ax,
                xticklabels=50, yticklabels=50)
    # Set the ticks and labels for each frame
    ax.set_xticks(xticks)
    ax.set_yticks(yticks)
    ax.set_xticklabels(xticklabels)
    ax.set_yticklabels(yticklabels)
    ax.set_xlabel('X (cm)')
    ax.set_ylabel('Y (cm)')
    ax.set_title(f'Time: {frame * 50} ms')


plt.ioff()  # Turn off interactive mode

data = np.load("diff_dose_arrays.npz")
start_row = 1000  #
end_row = 1200  #

# Create the list of arrays for the specified range
diff_dose_arrays = [data[f"arr_{i}"] for i in range(start_row, end_row)]

diff_dose_arrays = [data[key] for key in data.keys()]

# Prepare the custom colormap
colors = ["blue", "cyan", "yellow", (0, 1, 0)]  # End with bright green
cmap = LinearSegmentedColormap.from_list("custom_green", colors)

# Set up the figure and axis for the animation
fig, ax = plt.subplots(figsize=(20, 10))

# Customizing the tick labels to fit the spatial dimensions
xticks = np.linspace(0, diff_dose_arrays[0].shape[1], num=11)
yticks = np.linspace(0, diff_dose_arrays[0].shape[0], num=5)
xticklabels = [f"{x - 32.5}" for x in np.linspace(0, 65, num=11)]
yticklabels = [f"{10 - x * 10}" for x in np.linspace(0, 2, num=5)]

# Create the animation
anim = FuncAnimation(fig, update, frames=len(diff_dose_arrays), interval=50)

# Save the animation
anim.save('diff_dose_animation.gif', dpi=80, writer='imagemagick')

plt.close()  # Close the plot to prevent it from displaying statically

# Display the cummulation of the dose for a selected detector


# Coordinates of the detector to track
detector_row, detector_col = 20, 60  # indices

# Assuming detector_row, detector_col have been defined
# Extracting values for the selected detector across all frames
detector_values = [frame[detector_row, detector_col] for frame in diff_dose_arrays]
# Convert the list to a numpy array
detector_values = np.array(detector_values)

# Perform the division operation
detector_values = detector_values / 100  # Convert to cGy

cumulative_dose = np.cumsum(detector_values)

# Generate time points for each frame, 50 ms interval
time_points = np.arange(len(cumulative_dose)) * 50

# Setting up the figure for animation
fig, ax = plt.subplots()
ax.set_xlim(0, time_points[-1])  # Set x-axis to match the total duration
ax.set_ylim(0, np.max(cumulative_dose) * 1.1)  # Set y-axis slightly above the max cumulative dose
line, = ax.plot([], [], 'ro-', lw=2)  # Initialize the line plot

# Title and labels
ax.set_title('Cumulative Dose Over Time for Selected Detector')
ax.set_xlabel('Time (ms)')
ax.set_ylabel('Cumulative Dose')


# Initialization function: plot the background of each frame
def init():
    line.set_data([], [])
    return (line,)


# Animation update function, which is called for each frame
def update(frame):
    # Update the data of the line plot to extend to the current frame
    line.set_data(time_points[:frame + 1], cumulative_dose[:frame + 1])
    return (line,)


# Creating the animation
anim = FuncAnimation(fig, update, frames=len(cumulative_dose), init_func=init, blit=True, interval=50)

# Save the animation
anim.save('cumulative_dose_animation.gif', dpi=80, writer='imagemagick')

plt.close()  # Prevents the final frame from displaying statically

# Calculate the sum and max of values at intervals of 300
max_value = max(detector_values)
interval_sums = []
interval_bins = []
for i in range(0, int(max_value), 30):
    interval_values = [value for value in detector_values if i <= value < i + 300]
    interval_sum = sum(interval_values)
    interval_bin = i if interval_values else 0  # Use 0 as the max if the interval is empty
    interval_sums.append(interval_sum)
    interval_bins.append(interval_bin)

import seaborn as sns

# Convert interval_max_values to string for use as category labels
interval_max_values_str = [str(value) for value in interval_bins]

# Create the bar plot
sns.barplot(x=interval_max_values_str, y=interval_sums)

# Set the title and labels
plt.title('Sum of Interval Values for Each Max Value')
plt.xlabel('Max Value of Interval')
plt.ylabel('Sum of Interval Values')

# Display the plot
plt.show()
