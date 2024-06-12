import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load the data
file_path = r"P:\02_QA Equipment\02_ArcCheck\05_Commissoning\03_NROAC\Dose Rate Dependence Fix\Test on script\ACResultsPowerQuerySummary.txt"
data = pd.read_csv(file_path, sep='\t')

# Melt the data
data_melted = data.melt(id_vars=['Plan Name', '(mm)', 'Correction'],
                        value_vars=['3%3mm', '2%3mm', '1%3mm'],
                        var_name='Percentage', value_name='Value')

# Filter the data to only include 'Original' and 'DPP'
data_melted_filtered = data_melted[data_melted['Correction'].isin(['Original', 'DPP'])]

# Set the theme
sns.set_theme(style="white")

# Set up the matplotlib figure with smaller size
plt.figure(figsize=(20, 5))

plt.figure(figsize=(20, 5))
# Creating box plots with a custom color palette
palette = {'Original': '#1f77b4', 'DPP': '#2ca02c'}
y_limits = (75, data_melted_filtered['Value'].max() + 5)  # Set minimum value to 75 and adjust the max limit for clarity

for i, percentage in enumerate(['3%3mm', '2%3mm', '1%3mm'], start=1):
    plt.subplot(1, 3, i)
    sns.boxplot(x='Correction', y='Value', data=data_melted_filtered[data_melted_filtered['Percentage'] == percentage], palette=palette)
    plt.title(f'{percentage}', fontsize=12)  # Increase title font size
    plt.ylim(y_limits)
    plt.xticks(rotation=45, fontsize=10)  # Increase x-tick labels font size
    plt.yticks(fontsize=10)  # Increase y-tick labels font size
    plt.xlabel('')  # Remove x-axis label
    if i == 1:
        plt.ylabel('Pass Rates', fontsize=12)  # Set y-axis label
    else:
        plt.ylabel('')
    plt.legend([],[], frameon=False)

plt.tight_layout()
plt.show()