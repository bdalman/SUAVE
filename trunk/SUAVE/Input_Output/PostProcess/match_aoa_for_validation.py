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


def match_aoa_for_validation(analyses, results, aoa_targets, CM_FLAG=0, target_mach=1):
    """ Takes a list of input angles and the mission data structure, reruns the aerodynamics for the given AoAs 
    
        Assumptions:
        Passed a mission data structure with single_point mission segments to be used for running the new aerodynamics
        Single point missions are named sequentially starting with "single_point_1"
        	- Actually currently works with only one single_point, and just loops that one and pulls results out

        Inputs:
        	mission
       	    	single_point_segments
        	target_aoas                       [deg]
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
    target_AOA = aoa_targets
    num_sections = len(target_AOA)

    print('Passed in target AOA: ', target_AOA)

    #print(aero_analyses)
    #print(breakdown)


    if CM_FLAG ==1:
        stab_analyses = analyses.configs.base.stability

    # Initialize results variables you care about for plotting

    AOA = np.zeros(num_sections)
    CL  = np.zeros(num_sections)
    CD  = np.zeros(num_sections)
    CD_ind = np.zeros(num_sections)
    
    if CM_FLAG ==1:
        CM = np.zeros(num_sections)
        side_slip_state = state.conditions.aerodynamics.side_slip_angle
        mach_state = state.conditions.freestream.mach_number
        density_state = state.conditions.freestream.density




    for i in range(0, num_sections):
        state.conditions.aerodynamics.angle_of_attack = np.array([[target_AOA[i]]]) * Units.deg

        if CM_FLAG == 1:
            state.conditions.aerodynamics.side_slip_angle = np.array(side_slip_state)
            state.conditions.freestream.mach_number       = np.array(mach_state)
            state.conditions.freestream.density           = np.array(density_state)
        #state.conditions.aerodynamics
        #state.conditions.aerodynamics.angle_of_attack = target_AOA[i] * Units.deg

        #print(state.conditions.aerodynamics.angle_of_attack)

        new_results = aero_analyses.evaluate( state )


        #print(new_results)

        #print(breakdown)

        AOA[i] = target_AOA[i] * Units.deg  #This will convert it back to rads which SUAVE uses for everything except plotting, and numpy needs rads
        CL[i] = new_results.lift.total
        CD[i] = new_results.drag.total
        CD_ind[i] = new_results.drag.compressibility.total

        #print(new_results.drag)
        #print(new_results.lift)
        # if i == num_sections-1:
        #     print(breakdown)

        if CM_FLAG == 1:

            #### No surrogate method - AVL call functions are coded weirdly which necessitated this junk
            aoa = target_AOA[i] * Units.deg
            side_slip = state.conditions.aerodynamics.side_slip_angle
            mach = state.conditions.freestream.mach_number
            dens = state.conditions.freestream.density
            #velo = state.conditions.freestream.velocity

            state.conditions.aerodynamics.angle_of_attack = [aoa.item()]  # B/c of bad code, AVL function evaluation doesn't work on numpy objects, and VLM evaluation only works on numpy arrays
            state.conditions.aerodynamics.side_slip_angle = side_slip.item()
            state.conditions.freestream.mach_number       = mach.item()
            state.conditions.freestream.density           = dens.item()

            #print('AOA: ', state.conditions.aerodynamics.angle_of_attack, type(state.conditions.aerodynamics.angle_of_attack))
            #print('Side Slip: ', side_slip, type(side_slip))
            #print('Mach: ', mach, type(state.conditions.freestream.mach_number))

            results = stab_analyses.evaluate_conditions(state.conditions, False)
            CM[i] = results.aerodynamics.Cmtot[:,0]

            print('Neutral point: ', results.stability.static.neutral_point[:,0])
            
            #### Surrogate method for AVL, or normal method for Fid_zero
            # conds = state.conditions
            # stab_results = stab_analyses.__call__( conds )
            # CM[i] = stab_results.static.CM

            # print(stab_results)
            #print(breakdown)

    if CM_FLAG==0:
        CM = np.zeros(num_sections)
        return [AOA,CL,CD,CD_ind]
    elif CM_FLAG==1:
        return [AOA,CL,CD,CM]

    



