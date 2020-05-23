## @ingroup Input_Output-PostProcess
# plotting.py
# 
# Created:  Jul 2019, B. Dalman

# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------
import SUAVE
from SUAVE.Core import Units

import numpy as np
import matplotlib.pyplot as plt

#Set plot style at the top
#Good plot styles: seaborn, ggplot, classic(ok)
plt.style.use('default')


def plot_xy(x, y, x_label, y_label, plot_header, num_data_per_plot=1, labels=None, marker_flag=False, save_location=None, limits=None):
	""" Function that plots my data in whatever format is most appropriate

        Assumptions:
        Any required units are already correct

        Inputs:
        	x   - an nx1 vector of data for x-axis, or nxm matrix if there are > 1 data sets per plot
        	y   - an nx1 vector of data for y-axis, or nxm matrix if there are > 1 data sets per plot
        	x_label
        	y_label
        	plot_header 					  [string]
        	num_data_per_plot - how many lines/data sets to put on the plot [int]
        	labels 							  [vector of strings?]
        	save_location				      [optional]
        	fig_x_size 						  [optional]
        	fig_y_size 						  [optional]

        Outputs:
        	n/a

        Properties Used:
        N/A

        TODO: Expand (or add another function) to plot error bars and other kinds of plots
                                
    """

    # Unpack

    # Define plot title

	#fig = plt.figure( plot_header, figsize=(8,6) )
	fig = plt.figure( plot_header, figsize=(7,4) )
    # Define plot settings - font size, total plot size, etc
	plt.rc('font', size=10)

	# Actually plot now
	if labels[0] != None:
		for i in range(0, num_data_per_plot):
			if marker_flag:
				marker = marker_flag
			else:
				marker = pick_marker(i)

			marker += '-'
			plt.plot(x[:,i], y[:,i], marker, label=str(labels[i]))
		plt.legend(loc='best')
	else:
		if num_data_per_plot==1:
			if marker_flag:
				marker = marker_flag
			else:
				marker = pick_marker(0)
			plt.plot(x[:], y[:], marker)
		else:
			for i in range(0, num_data_per_plot):
				if marker_flag:
					marker = marker_flag
				else:
					marker = pick_marker(i)
				plt.plot(x[:,i], y[:,i], marker)

	plt.xlabel(x_label)
	plt.ylabel(y_label)
	plt.grid(True)

	plt.axis() # TODO: Implement bound setting

	if not limits==None:
		ax = plt.axes()

		ax.set_xlim(limits[0],limits[1])
		ax.set_ylim(limits[3],limits[4])
		#ax.grid(False)
		ax.xaxis.set_major_locator(plt.MultipleLocator(limits[2]))
		ax.yaxis.set_major_locator(plt.MultipleLocator(limits[5]))


	# Save OR show plots here, TODO: Improve this with more options
	if save_location:
		plt.savefig(save_location + plot_header + '.eps')
	else:
	    plt.show()


	return

def plot_xy_errors(x, y, x_errors, y_errors, x_label, y_label, plot_header, num_data_per_plot=1, num_errors_given=1, labels=None, save_location=None, limits=None):
	""" Function that plots my data in whatever format is most appropriate, with the first columns of data being plotted with error bars, and the rest with lines

        Assumptions:
        	-Any required units are already correct
        	-The x/y data for which errors are included are the first columns of the matrix


        Inputs:
        	x   - an nx1 vector of data for x-axis, or nxm matrix if there are > 1 data sets per plot
        	y   - an nx1 vector of data for y-axis, or nxm matrix if there are > 1 data sets per plot
        	errors - an nxm matrix, where m_errors =< m_x_matrix
        	x_label
        	y_label
        	plot_header 					  [string]
        	num_data_per_plot - how many lines/data sets to put on the plot [int]
        	labels 							  [vector of strings?]
        	save_location				      [optional]
        	fig_x_size 						  [optional]
        	fig_y_size 						  [optional]
        	limits - list of 6 inputs         [optional]
        		   - 1,2,4,5 are x/y lower and upper limits. 3 & 6 are x and y spacing

        Outputs:
        	n/a

        Properties Used:
        N/A

        TODO: Expand (or add another function) to plot error bars and other kinds of plots
                                
    """
    #This line doesn't actually work :(
	#plt.rcParams.update({'font.family': "Times New Roman"})

    # Unpack
	num_errors = num_errors_given  # TODO: Rewrite function to work with more than one set of errors plotted!

    # Define plot title
	fig = plt.figure( plot_header, figsize=(7,4) )
    # Define plot settings - font size, total plot size, etc
	plt.rc('font', size=10)

	# Actually plot now
	if len(labels)>0:
		for i in range(0, num_errors):
			marker = pick_marker(i)
			plt.errorbar(x[:,i], y[:,i], fmt=marker, xerr=x_errors[:], yerr=y_errors, label=str(labels[i]))

		for i in range(num_errors, num_data_per_plot):
			marker = pick_marker(i)
			marker += '-'
			plt.plot(x[:,i], y[:,i], marker, label=str(labels[i]))
		plt.legend(loc='best')
	else:
		for i in range(0, num_errors):
			marker = pick_marker(i)
			plt.errorbar(x[:,i], y[:,i], fmt=marker, xerr=x_errors[:], yerr=y_errors)
		for i in range(num_errors, num_data_per_plot):
			marker = pick_marker(i)
			marker += '-'
			plt.plot(x[:,i], y[:,i], marker)

	plt.xlabel(x_label)
	plt.ylabel(y_label)
	plt.grid(True)

	plt.axis() # TODO: Implement bound setting

	if not limits==None:
		ax = plt.axes()

		ax.set_xlim(limits[0],limits[1])
		ax.set_ylim(limits[3],limits[4])
		#ax.grid(False)
		ax.xaxis.set_major_locator(plt.MultipleLocator(limits[2]))
		ax.yaxis.set_major_locator(plt.MultipleLocator(limits[5]))

		#ax.yaxis.set_major_locator(plt.LinearLocator(7))
		#ax.xaxis.set_major_locator(plt.FixedLocator([-1, 0, 5, 10, 15, 20, 22]))


	# Save OR show plots here, TODO: Improve this with more options
	if save_location:
		plt.savefig(save_location + plot_header + '.eps')
	else:
		plt.show()

	return



# ---------------------------------------------------------------------------------------------
# Helper functions

def pick_marker(index):
	marker_types = np.array(['ko', 'bv', 'r^', 'cx', 'm1', 'ys', 'g*'])
	#marker_types = np.array(['bv', 'r^', 'cx', 'm1', 'ys', 'g*'])

	try:
		marker_selection = str(marker_types[index])
	except:
		print('Plotting marker index too high! Current system can only plot seven different markers!')

	return marker_selection











