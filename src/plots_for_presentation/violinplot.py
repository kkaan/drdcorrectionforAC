import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load the data
file_path = (r"P:\02_QA Equipment\02_ArcCheck\05_Commissoning\03_NROAC\Dose Rate Dependence Fix\Test on "
             r"script\ACResultsPowerQuerySummary.csv")
data = pd.read_csv(file_path)

# Combine the split columns for easier manipulation
data['Measured: Diode Array Calc shift (mm)'] = data['Measured: Diode Array'] + ' ' + data['Calc shift (mm)']

# Drop the original split columns
data_corrected = data.drop(columns=['Measured: Diode Array', 'Calc shift (mm)'])

# Melt the data
data_melted = data_corrected.melt(id_vars=['Measured: Diode Array Calc shift (mm)', 'Correction'],
                                  value_vars=['3%, 3mm', '2%, 3mm', '1%, 3mm'],
                                  var_name='Percentage', value_name='Value')

# Set up the matplotlib figure
plt.figure(figsize=(15, 5))

# Creating violin plots
for i, percentage in enumerate(['3%, 3mm', '2%, 3mm', '1%, 3mm'], start=1):
    plt.subplot(1, 3, i)
    sns.violinplot(x='Correction', y='Value', data=data_melted[data_melted['Percentage'] == percentage])
    plt.title(f'Violin Plot for {percentage}')
    plt.xticks(rotation=45)

plt.tight_layout()
plt.show()
