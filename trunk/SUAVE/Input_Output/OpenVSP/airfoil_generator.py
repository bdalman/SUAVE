# airfoil_generator.py

#Takes inputs of point location, and outputs an airfoil file, formatted for vsp airfoils (.af)

import numpy as np


def main(top_file, bottom_file, top_points, bottom_points, airfoil_name):
	"""Takes inputs of known wedge/shape points, and generates a vsp compatible airfoil foil using cosine spacing. Intended to make airfoil files for arbitrary points
	Not yet compatible with SUAVE structure, but a useful prep tool for custom airfoil files
    Airfoil points should be normalized (0,1) in the x direction

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
    filename = airfoil_name + '.af'

    f = open(filename, mode='w')

    f.write(str(airfoil_name) + ' AIRFOIL FILE')
    f.write(str(airfoil_name))
    f.write('0  Sym Flag')
    #f.write(str(top_points) + ' Num Pnts Uppper')
    #f.write(str(bottom_points) + '  Num Pnts Lower')

    # Calculate x/y point locations across the airfoil top

    beta = np.linspace(0,np.pi, top_points)
    x_top =    0.5 .* (1 - np.cos(beta))
    y_top = np.zeros(top_points,1)

    if top_data_len == 2:
        y_top_slope = (top_data_y[1] - top_data_y[0])/ (top_data_x[1] - top_data_x[0])
        for i in range(0, top_points):
            y_top[i] = top_data_y[0] + y_top_slope * x_top
    elif top_data_len >= 3:
        print('Need to update script for other ')


    x_bot =    0.5 .* (1 - np.cos(beta))
    y_bot = np.zeros(bottom_points,1)

    if bottom_data_len == 2:
        y_bot_slope = (bottom_data_y[1] - bottom_data_y[0])/ (bottom_data_x[1] - bottom_data_x[0])
        for i in range(0, bottom_points):
            y_bot[i] = bottom_data_y[0] + y_bottom_slope * x_bot
    elif bottom_data_len == 3:
        x_bot_1 = x_bot * bottom_data_x[1]
        x_bot_2 = 0.5 .* (1 - np.cos(beta)) * (bottom_data_x[2] - bottom_data_x[1]) + bottom_data_x[1]

        y_bot_slope_1 = (bottom_data_y[1] - bottom_data_y[0])/ (bottom_data_x[1] - bottom_data_x[0])
        y_bot_slope_2 = (bottom_data_y[2] - bottom_data_y[1])/ (bottom_data_x[2] - bottom_data_x[1])

        y_bot_2 = zeros(bottom_points, 1)

        for i in range(0, bottom_data_len):
            y_bot[i] = 
























main()