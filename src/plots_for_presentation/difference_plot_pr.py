import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load data
file_path = r'P:\02_QA Equipment\02_ArcCheck\05_Commissoning\03_NROAC\Dose Rate Dependence Fix\Test on script\ACResultsPowerQuerySummary.txt'
df = pd.read_csv(file_path, delimiter='\t')

# Ensure numeric columns are converted from strings to numbers
for col in ['3%3mm', '2%3mm', '1%3mm']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Split data into Original and PR correction
original_df = df[df['Correction'] == 'Original'].set_index('Plan Name')
pr_df = df[df['Correction'] == 'PR'].set_index('Plan Name')

# Melt the original and PR dataframes
original_melted = original_df.reset_index().melt(id_vars=['Plan Name'], value_vars=['3%3mm', '2%3mm', '1%3mm'], var_name='Metric', value_name='Original')
pr_melted = pr_df.reset_index().melt(id_vars=['Plan Name'], value_vars=['3%3mm', '2%3mm', '1%3mm'], var_name='Metric', value_name='PR')

metrics = ['3%3mm', '2%3mm', '1%3mm']

for i, metric in enumerate(metrics):
    # Create the plot for each metric
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.set(style="whitegrid")

    # Plot the original values
    subset_df = original_melted[original_melted['Metric'] == metric]
    sns.scatterplot(x=subset_df['Original'], y=subset_df['Plan Name'], color='darkgrey', legend=False, s=100, marker='o', alpha=0.5, ax=ax)

    # Plot the PR values
    subset_df = pr_melted[pr_melted['Metric'] == metric]
    sns.scatterplot(x=subset_df['PR'], y=subset_df['Plan Name'], color='darkblue', legend=False, s=100, marker='o', alpha=0.5, ax=ax)

    # Set the limits for the x-axis and set label color to dark grey
    ax.set_xlim([50, 110])
    ax.set_xlabel('Pass Rates', color='darkgrey')

    # Add labels and title
    ax.set_ylabel('Plan Name')
    ax.set_title(f'PR {metric}', loc='left')  # Set title to just the metric and align left

    plt.tight_layout()
    plt.savefig(f'PR_{metric}_pass_rate_plot.png', dpi=300)
    plt.show()