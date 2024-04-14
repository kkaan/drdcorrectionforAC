import numpy as np
from read_acl_file import read_detector_file, detector_arrays
from plots import create_animation, stacked_histogram
from diode_numbers_in_snc_array import diode_numbers_in_snc_array

stacked_histogram(dose_accumulated_df, dose_rate_df, [630, 610, 590, 570, 550])



