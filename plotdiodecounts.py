import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import seaborn as sns

# Load the data, skipping the first two rows and using the next two for corrections
file_path = r"P:\02_QA Equipment\02_ArcCheck\05_Commissoning\03_NROAC\Dose Rate Dependence Fix\Test on script\timeseries.csv"
data = pd.read_csv(file_path, header=None, skiprows=2)

# Extract background correction and sensitivity correction factors
background_correction = data.iloc[0, :].values
sensitivity_correction = data.iloc[1, :].values

# Apply corrections to the raw data
corrected_data = (data.iloc[2:] - background_correction) / sensitivity_correction

# Calculate cumulative counts
cumulative_counts = corrected_data.cumsum()

# Set the style of seaborn
sns.set_style("darkgrid")

# Initialize the figure
fig, ax = plt.subplots()

def animate(i):
    ax.clear()  # Clear the axis to redraw
    sns.lineplot(data=cumulative_counts.iloc[:i+1], dashes=False, ax=ax, legend='full')
    ax.set_xlabel('Time (50ms intervals)')
    ax.set_ylabel('Cumulative Counts')
    ax.set_title('Accumulated Counts over Time for Detectors 1-5')

# Creating the animation
ani = animation.FuncAnimation(fig, animate, frames=len(cumulative_counts), interval=50, repeat=False)

# Save the animation
ani.save('accumulated_counts.gif', writer='pillow', dpi=300)




