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


def mach_and_aoa_sweep(analyses, results, mach_targets, aoa_target):
    """ Takes a list of input machs, an AoA, and the mission data structure, reruns the aerodynamics for the given AoA and machs 
    
        Assumptions:
        Passed a mission data structure with single_point mission segments to be used for running the new aerodynamics
        Single point missions are named sequentially starting with "single_point_1"
        	- Actually currently works with only one single_point, and just loops that one and pulls results out

        Inputs:
        	mission
       	    	single_point_segments
        	target_aoa                       [deg]
            mach_targets                     [unitless]
            CM_FLAG ---- 0 for no
                         1 for yes

        Outputs:
        	AoA 							  [deg]
        	CL
        	CD
            CM

        Properties Used:
        N/A

        TODO: -Fix comments with new version
        TODO: -Output whole drag and lift structures?
                                
    """

    # Unpack

    aero_analyses = analyses.configs.base.aerodynamics
    state = results.segments.single_point_1.state
    target_AOA = aoa_target
    target_machs = mach_targets

    num_sections = len(target_machs)

    print('Passed in target Machs: ', target_machs)

    # Initialize results variables you care about for plotting

    AOA = np.zeros(num_sections)
    CL  = np.zeros(num_sections)
    CD  = np.zeros(num_sections)


    for i in range(0, num_sections):
        state.conditions.aerodynamics.angle_of_attack = np.array([[target_AOA]]) * Units.deg
        state.conditions.freestream.mach_number         = np.array([[target_machs[i]]])

        new_results = aero_analyses.evaluate( state )


        #print(breakdown)

        #print(new_results)

        #print(breakdown)

        AOA[i] = target_AOA * Units.deg  #This will convert it back to rads which SUAVE uses for everything except plotting, and numpy needs rads
        CL[i] = new_results.lift.total
        CD[i] = new_results.drag.total

        #print(new_results.drag.keys())
        #print(new_results.drag.compressibility)
        # if i == num_sections-1:
        #     print(breakdown)



    return [AOA,CL,CD]

    



