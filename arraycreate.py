import numpy as np

# Step 1: Create an initial array of size 41x131 filled with zeros
array = np.zeros((41, 131))

# Step 2: Fill every second row and column with integers from 1 to 1386
# Starting from the bottom left corner (which in array indexing is the last row, first column)
number = 1
for row in range(40, -1, -2):  # Start from the last row, move upwards in steps of 2
    for col in range(0, 131, 2):  # Start from the first column, move right in steps of 2
        if number <= 1386:
            array[row, col] = number
            number += 1
        else:
            break  # Stop if the number exceeds 1386

array = array.astype(int)
# Since Python indexing starts at 0, "even" rows and columns as per normal counting are actually odd-indexed in Python
# This approach automatically leaves even-indexed rows and columns (starting from 0) as zeros, as required
print(array)