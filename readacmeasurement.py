import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()  # Hide the main window

# Define filters
filter1 = [('ACM files', '*.acm')]
filter2 = [('Text files', '*.txt')]

# Ask user to select .acm file
acm_file_path = filedialog.askopenfilename(filetypes=filter1, title='Bitte .acm-Datei auswählen')

# Ask user to select .txt file
txt_file_path = filedialog.askopenfilename(filetypes=filter2, title='Bitte .txt-Datei auswählen')

# Display selected file paths
print("Selected ACM file:", acm_file_path)
print("Selected TXT file:", txt_file_path)