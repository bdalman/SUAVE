## @ingroup Methods-Performance
# estimate_wing_bending_moment.py
#
# Created:  May 2019, B. Dalman

# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------

import SUAVE
from   SUAVE.Core            import Data
from   SUAVE.Core            import Units

import numpy as np

# ----------------------------------------------------------------------
#  Compute wing bending moment
# ----------------------------------------------------------------------

def estimate_wing_bending_moment(vehicle):
	''' Method taken from MIT OCW Aeronautics & Astronautics - Lab 10 Lecture Notes (Wing Bending Calculations)

	This calculates wing bending moment assuming steady, level flight. Higher loads can be accounted for by increasing the loading factor

	'''


	# Unpack
	fuse_weight = vehicle.mass_properties.fuselage_weight
	wing_area   = vehicle.wings['main_wing'].areas.reference
	wing_root_chord = vehicle.wings['main_wing'].chords.root
	wing_span 		= vehicle.wings['main_wing'].spans.projected
	wing_le_sweep 	= vehicle.wings['main_wing'].Segments[0].sweeps.leading_edge
	wing_ar_first_segment = vehicle.wings['main_wing'].Segments[0].aspect_ratio
	wing_segment_taper 	= vehicle.wings['main_wing'].Segments[0].taper

	num_sections = len(vehicle.wings['main_wing'].Segments)
	num_sec_less_one = num_sections - 1 
	q 		= np.zeros(num_sections) 		# Wing load on each wing section
	q_cent 	= np.zeros(num_sections)  		# Centroid of each load section
	chords  = np.zeros(num_sections)
	spans   = np.zeros(num_sections)
	q_placeholder = 0

	#Fill in some wing section parameters
	for i in range(0, num_sections):
		chords[i] = vehicle.wings['main_wing'].Segments[i].root_chord_percent
		spans[i]  = vehicle.wings['main_wing'].Segments[i].percent_span_location


	# Calculations
	N = 1.0 	# Loading factor, 1 for level flight
	K = N * fuse_weight / wing_area

	# Calculate load across wing with q = K * c(y), then find bending moment based off distance from root to centroid of force
	for i in range(0, num_sec_less_one):
		h = spans[i+1] - spans[i]
		q[i] = (chords[i]-chords[i+1])*wing_root_chord * (h) * K    # Don't have to use total span because that's accounted for in K already
		q_cent[i] = wing_span * h * (2*chords[i+1] + chords[i])/(3*(chords[i+1]+chords[i]))  + wing_span * spans[i]

	q_tot = np.sum(q) # Total wing loading

	for i in range(0, num_sec_less_one):
		q_placeholder = q_placeholder + q[i]*q_cent[i]

	q_y_location = q_placeholder/q_tot

	#For a highly swept wing, we also have a CP that's further back, which adds a twist around the y-axis.
	# We start by finding the half-chord sweep of the first segment, and then use that to find the x-distance from the y-distance already found
	wing_hc_sweep = np.arctan(np.tan(wing_le_sweep) - (4./wing_ar_first_segment)*(0.5-0.)*(1.-wing_segment_taper)/(1.+wing_segment_taper))

	# For a diamond airfoil, we assume the CP is close to the center/half chord

	q_x_location = np.tan(wing_hc_sweep) * q_y_location


	# For total bending moment

	q_location = np.sqrt(q_x_location**2 + q_y_location**2)



	# Finally, we get

	print('WBM Debugging: ', q, q_cent, q_tot, q_location)

	wing_bending_moment = (q_tot * q_location) / wing_root_chord


	return wing_bending_moment

