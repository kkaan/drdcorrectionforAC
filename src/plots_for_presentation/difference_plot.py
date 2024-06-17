import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib as mpl

# Load data
file_path = r'P:\02_QA Equipment\02_ArcCheck\05_Commissoning\03_NROAC\Dose Rate Dependence Fix\Test on script\ACResultsPowerQuerySummary.txt'
df = pd.read_csv(file_path, delimiter='\t')

# Ensure numeric columns are converted from strings to numbers
for col in ['3%3mm', '2%3mm', '1%3mm']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Split data into Original and PR correction
original_df = df[df['Correction'] == 'Original'].set_index('Plan Name')
pr_df = df[df['Correction'] == 'PR'].set_index('Plan Name')


# Check if data is numeric
if (original_df[['3%3mm', '2%3mm', '1%3mm']].dtypes == 'float64').all() and (pr_df[['3%3mm', '2%3mm', '1%3mm']].dtypes == 'float64').all():
    # Calculate differences
    difference_df = pr_df[['3%3mm', '2%3mm', '1%3mm']].subtract(original_df[['3%3mm', '2%3mm', '1%3mm']])
else:
    print("Data is not numeric. Cannot perform subtraction.")


# Reset index to use for plotting
difference_df.reset_index(inplace=True)

# Melt the dataframe for seaborn plotting
melted_df = difference_df.melt(id_vars=['Plan Name'], value_vars=['3%3mm', '2%3mm', '1%3mm'], var_name='Metric', value_name='Difference')

# Define a function to map the improvement/deterioration to colors
def color_mapper(val):
    if val >= 0:
        return 'green'
    else:
        return 'red'

# Melt the original and PR dataframes
original_melted = original_df.reset_index().melt(id_vars=['Plan Name'], value_vars=['3%3mm', '2%3mm', '1%3mm'], var_name='Metric', value_name='Original')
pr_melted = pr_df.reset_index().melt(id_vars=['Plan Name'], value_vars=['3%3mm', '2%3mm', '1%3mm'], var_name='Metric', value_name='PR')

import matplotlib as mpl

import matplotlib as mpl

# Create the plot
fig, axs = plt.subplots(3, 1, figsize=(10, 24))
sns.set(style="whitegrid")

metrics = ['3%3mm', '2%3mm', '1%3mm']

for i, metric in enumerate(metrics):
    # Create the plot for each metric
    fig, ax1 = plt.subplots(figsize=(10, 8))
    sns.set(style="whitegrid")

    # Plot the differences
    subset_df = melted_df[melted_df['Metric'] == metric]
    colors = subset_df['Difference'].apply(color_mapper)
    sns.scatterplot(x=subset_df['Difference'], y=subset_df['Plan Name'], hue=colors, palette=['red', 'green'], legend=False, s=100, marker='^', ax=ax1)

    # Set the limits for the first x-axis and set label color to dark grey
    ax1.set_xlim([-10, 10])
    ax1.set_xlabel('Differences', color='darkgrey')

    # Reduce the font size
    mpl.rcParams.update({'font.size': 10})

    # Create a second x-axis
    ax2 = ax1.twiny()

    # Plot the original values
    subset_df = original_melted[original_melted['Metric'] == metric]
    sns.scatterplot(x=subset_df['Original'], y=subset_df['Plan Name'], color='darkgrey', legend=False, s=100, marker='o', alpha=0.5, ax=ax2)

    # Plot the PR values
    subset_df = pr_melted[pr_melted['Metric'] == metric]
    sns.scatterplot(x=subset_df['PR'], y=subset_df['Plan Name'], color='darkblue', legend=False, s=100, marker='o', alpha=0.5, ax=ax2)

    # Set the limits for the second x-axis and set label color to dark grey
    ax2.set_xlim([50, 110])
    ax2.set_xlabel('Pass Rates', color='darkgrey')

    # Add labels and title
    ax1.set_ylabel('Plan Name')
    ax1.set_title(f'PR {metric}', loc='left')  # Set title to just the metric and align left
    ax1.axvline(0, color='gray', linestyle='--')

    plt.tight_layout()
    plt.ioff()
    plt.savefig(f'PR_{metric}_correction_plot.png', dpi=300)




# Load data for DPP correction
dpp_df = df[df['Correction'] == 'DPP'].set_index('Plan Name')

# Check if data is numeric
if (original_df[['3%3mm', '2%3mm', '1%3mm']].dtypes == 'float64').all() and (dpp_df[['3%3mm', '2%3mm', '1%3mm']].dtypes == 'float64').all():
    # Calculate differences
    difference_dpp_df = dpp_df[['3%3mm', '2%3mm', '1%3mm']].subtract(original_df[['3%3mm', '2%3mm', '1%3mm']])
else:
    print("Data is not numeric. Cannot perform subtraction.")

# Reset index to use for plotting
difference_dpp_df.reset_index(inplace=True)

# Melt the dataframe for seaborn plotting
melted_dpp_df = difference_dpp_df.melt(id_vars=['Plan Name'], value_vars=['3%3mm', '2%3mm', '1%3mm'], var_name='Metric', value_name='Difference')

# Melt the DPP dataframe
dpp_melted = dpp_df.reset_index().melt(id_vars=['Plan Name'], value_vars=['3%3mm', '2%3mm', '1%3mm'], var_name='Metric', value_name='DPP')

# Create the plot for DPP
fig, axs = plt.subplots(3, 1, figsize=(10, 24))
sns.set(style="whitegrid")

for i, metric in enumerate(metrics):
    metrics = ['3%3mm', '2%3mm', '1%3mm']

    for i, metric in enumerate(metrics):
        # Create the plot for each metric
        fig, ax1 = plt.subplots(figsize=(10, 8))
        sns.set(style="whitegrid")

        # Plot the differences
        subset_df = melted_dpp_df[melted_df['Metric'] == metric]
        colors = subset_df['Difference'].apply(color_mapper)
        sns.scatterplot(x=subset_df['Difference'], y=subset_df['Plan Name'], hue=colors, palette=['green', 'red'],
                        legend=False, s=100, marker='^', ax=ax1)

        # Set the limits for the first x-axis and set label color to dark grey
        ax1.set_xlim([-10, 10])
        ax1.set_xlabel('Differences', color='darkgrey')

        # Reduce the font size
        mpl.rcParams.update({'font.size': 10})

        # Create a second x-axis
        ax2 = ax1.twiny()

        # Plot the original values
        subset_df = original_melted[original_melted['Metric'] == metric]
        sns.scatterplot(x=subset_df['Original'], y=subset_df['Plan Name'], color='darkgrey', legend=False, s=100,
                        marker='o', alpha=0.5, ax=ax2)

        # Plot the PR values
        subset_df = dpp_melted[dpp_melted['Metric'] == metric]
        sns.scatterplot(x=subset_df['DPP'], y=subset_df['Plan Name'], color='darkblue', legend=False, s=100, marker='o',
                        alpha=0.5, ax=ax2)

        # Set the limits for the second x-axis and set label color to dark grey
        ax2.set_xlim([50, 110])
        ax2.set_xlabel('Pass Rates', color='darkgrey')

        # Add labels and title
        ax1.set_ylabel('Plan Name')
        ax1.set_title(f'DPP {metric}', loc='left')  # Set title to just the metric and align left
        ax1.axvline(0, color='gray', linestyle='--')

        plt.tight_layout()
        plt.ioff()
        plt.savefig(f'DPP_{metric}_correction_plot.png', dpi=300)

