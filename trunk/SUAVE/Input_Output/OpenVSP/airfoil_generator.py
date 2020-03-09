# airfoil_generator.py

#Takes inputs of point location, and outputs an airfoil file, formatted for vsp airfoils (.af)

import numpy as np


def main(top_file, bottom_file, top_points, bottom_points, output_file):
	"""Takes inputs of known wedge/shape points, and generates a vsp compatible airfoil foil using cosine spacing. Intended to make airfoil files for arbitrary points
	Not yet compatible with SUAVE structure, but a useful prep tool for custom airfoil files

    Assumptions:
    None

    Source:
    N/A

    Inputs:
    Airfoil points file location for top points
    Airfoil points file location for bottom points
    Number of points along top of airfoil (to generate)
    Number of points along bottom of airfoil (to generate)
    Output file name

    Outputs:
    <tag>.af            An airfoil file for OpenVSP

    Properties Used:
    N/A
    """    

    top_data = np.loadtxt(top_file)
    bottom_data = np.loadtxt(bottom_file)

    top_data_x = top_data[0,:]
    top_data_y = top_data[1,:]

    bottom_data_x = bottom_data[0,:]
    bottom_data_y = bottom_data[1,:]

    top_data_len = len(top_data_x)
    bottom_data_len = len(bottom_data_x)

    # Open file, write header

    
























main()