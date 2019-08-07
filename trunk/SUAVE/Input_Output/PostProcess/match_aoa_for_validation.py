## @ingroup Input_Output-PostProcess
# match_aoa_for_validation.py
# 
# Created:  Jul 2019, B. Dalman

# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------
import SUAVE
from SUAVE.Core import Units

import numpy as np


def match_aoa_for_validation(analyses, results, aoa_targets):
    """ Takes a list of input angles and the mission data structure, reruns the aerodynamics for the given AoAs 
    
        Assumptions:
        Passed a mission data structure with single_point mission segments to be used for running the new aerodynamics
        Single point missions are named sequentially starting with "single_point_1"
        	- Actually currently works with only one single_point, and just loops that one and pulls results out

        Inputs:
        	mission
       	    	single_point_segments
        	target_aoas                       [deg]

        Outputs:
        	AoA 							  [deg]
        	CL
        	CD

        Properties Used:
        N/A

        TODO: -Fix comments with new version
        TODO: -Output whole drag and lift structures?
                                
    """

    # Unpack

    aero_analyses = analyses.configs.base.aerodynamics
    state = results.segments.single_point_1.state
    target_AOA = aoa_targets
    num_sections = len(target_AOA)

    print('Passed in target AOA: ', target_AOA)

    #print(aero_analyses)
    #print(breakdown)


    # Initialize results variables you care about for plotting

    AOA = np.zeros(num_sections)
    CL  = np.zeros(num_sections)
    CD  = np.zeros(num_sections)

    for i in range(0, num_sections):
    	state.conditions.aerodynamics.angle_of_attack = np.array([[target_AOA[i]]]) * Units.deg

    	#print(state.conditions.aerodynamics.angle_of_attack)

    	new_results = aero_analyses.evaluate( state )

    	#print(new_results)

    	#print(breakdown)

    	AOA[i] = target_AOA[i] * Units.deg   #This will convert it back to rads which SUAVE uses for everything except plotting, and numpy needs rads
    	CL[i] = new_results.lift.total
    	CD[i] = new_results.drag.total


    return [AOA, CL, CD]



