import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# Create legend handles manually
legend_elements = [Line2D([0], [0], marker='o', color='w', markerfacecolor='darkblue', markersize=10, label='Pass Rate Corrected'),
                   Line2D([0], [0], marker='o', color='w', markerfacecolor='darkgrey', markersize=10, label='Pass Rate Uncorrected'),
                   Line2D([0], [0], marker='^', color='w', markerfacecolor='green', markersize=10, label='Pass Rate Difference Better'),
                   Line2D([0], [0], marker='^', color='w', markerfacecolor='red', markersize=10, label='Pass Rate Difference Worse')]

# Create the figure and the axes
fig, ax = plt.subplots()

# Add the legend to the plot
ax.legend(handles=legend_elements, loc='center')

# Hide axes
ax.axis('off')
plt.savefig(f'legend.png', dpi=300)
plt.show()