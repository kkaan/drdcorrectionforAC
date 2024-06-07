import sys
import os

# Add the src directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src import io_snc

def main():
    """
    main function to fix measured files

    Returns
    -------

    """
    # ask user for file path of measured file
    file_path = input("Please enter the file path: ")
    return file_path


if __name__ == "__main__":
    main()