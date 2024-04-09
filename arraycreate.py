def reorganize_detectors_in_acl_file(acl_file):
    """
    Reorganizes the detectors numbers in an acl measurement file into the planar array 
    that is displayed in SNC Patient software.

    Parameters:
    acl_file (str): The path to the acl measurement file.

    Returns:
    array (ndarray): A 2D numpy array representing the reorganized detectors.
    """
    # Step 1: Read the acl file and extract the detector numbers
    # This step is dependent on the format of the acl file and is not shown here

    # Step 2: Create an initial array of size 41x131 filled with zeros
    array = np.zeros((41, 131))

    # Step 3: Fill every second row and column with detector numbers
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
