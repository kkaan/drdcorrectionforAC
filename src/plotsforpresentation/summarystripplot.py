import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load the data
file_path = (r"P:\02_QA Equipment\02_ArcCheck\05_Commissoning\03_NROAC\Dose Rate Dependence Fix\Test on "
             r"script\ACResultsPowerQuerySummary.txt")
data = pd.read_csv(file_path, sep='\t')

# Melt the data
data_melted = data.melt(id_vars=['Plans', 'Correction'],
                        value_vars=['3%, 3mm', '2%, 3mm', '1%, 3mm'],
                        var_name='Percentage', value_name='Value')

# Set the theme
sns.set_theme(style="whitegrid")

# Set up the matplotlib figure
plt.figure(figsize=(15, 5))

# Creating strip plots with a custom color palette
palette = {'none': '#1f77b4', 'DPP': '#2ca02c', 'PR': '#17becf'}
x_limits = (80, data_melted['Value'].max() + 5)  # Set minimum value to 80 and adjust the max limit for clarity

for i, percentage in enumerate(['3%, 3mm', '2%, 3mm', '1%, 3mm'], start=1):
    plt.subplot(1, 3, i)
    sns.stripplot(x='Value', y='Plans', data=data_melted[data_melted['Percentage'] == percentage],
                  hue='Correction', palette=palette, dodge=True, jitter=True)
    plt.title(f'{percentage}', fontsize=12)  # Increase title font size
    plt.xlim(x_limits)
    plt.xticks(rotation=45, fontsize=10)  # Increase x-tick labels font size
    plt.yticks(fontsize=10)  # Increase y-tick labels font size
    plt.grid(axis='x')  # Add horizontal grid lines
    for j in range(len(data['Plans'].unique())):
        plt.axhline(y=j, color='gray', linestyle='--', linewidth=0.7)
    if i == 1:
        plt.xlabel('Pass Rates', fontsize=12)  # Set x-axis label
    else:
        plt.xlabel('')
    plt.ylabel('')  # Remove y-axis label
    plt.legend(title='Correction', fontsize=10, title_fontsize=12, loc='best')

plt.tight_layout()
plt.show()