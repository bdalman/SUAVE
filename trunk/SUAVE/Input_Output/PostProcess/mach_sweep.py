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
import copy


def mach_sweep(analyses, mach_targets, verbose=True):
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

    #aero_analyses = analyses.configs.base.aerodynamics
    state = analyses.missions.base.segments[0].state
    place_holder = copy.deepcopy(analyses)
    #print(breakdown)

    #print(place_holder)
    #print(breakdown)
    conditions = state.conditions
    target_speeds = mach_targets
    num_sections = len(target_speeds[0])

    if verbose:
        print('Passed in target speeds: ', target_speeds[0])


    # Initialize results variables you care about for plotting

    aoa = np.zeros(num_sections)
    drag = np.zeros(num_sections)
    lift = np.zeros(num_sections)
    speed = np.zeros(num_sections)
    mach = np.zeros(num_sections)
    temp = np.zeros(num_sections)
    pres = np.zeros(num_sections)
    dynamic_pres = np.zeros(num_sections)
    stag_temp = np.zeros(num_sections)
    stag_pres = np.zeros(num_sections)

    thrust_required = np.zeros(num_sections)
    tsfc = np.zeros(num_sections)
    specific_impulse = np.zeros(num_sections)
    throttle        = np.zeros(num_sections)

    for i in range(0, num_sections):
        analyses.missions.base.segments[0].air_speed = target_speeds[0][i]
        #print(analyses.missions.base.segments[0].altitude)
        #print(breakdown)

        ## Commented out analyses.finalize() - better option is probably just to complete before pass in
        ## The reason to comment out is if a mission with a surrogate was passed in, it was recreating the surrogate every time, which is substantially more expensive then just solving w/o surrogate
        # analyses.finalize()

        mission = analyses.missions.base

        new_results = mission.evaluate()

        #Plane chars to save

        
        aoa[i] = new_results.segments[0].conditions.aerodynamics.angle_of_attack
        drag[i] = -1 * new_results.segments[0].conditions.frames.wind.drag_force_vector[:,0]
        lift[i] = -1 * new_results.segments[0].conditions.frames.wind.lift_force_vector[:,2]
        speed[i] = target_speeds[0][i]
        mach[i] = new_results.segments[0].conditions.freestream.mach_number
        temp[i] = new_results.segments[0].conditions.freestream.temperature
        pres[i] = new_results.segments[0].conditions.freestream.pressure
        dynamic_pres[i] = new_results.segments[0].conditions.freestream.dynamic_pressure
        stag_temp[i] = new_results.segments[0].conditions.freestream.stagnation_temperature
        stag_pres[i] = new_results.segments[0].conditions.freestream.stagnation_pressure


        if verbose:
            print('For speed of :', new_results.segments[0].conditions.freestream.mach_number)
            print('Lift coef is: ', new_results.segments[0].conditions.aerodynamics.lift_coefficient)

        #print(new_results.segments[0].conditions.aerodynamics.drag_breakdown)
        #print(new_results.segments[0].conditions.aerodynamics.lift_coefficient)
        #if i==1:
        #    print(breakdown)

        keys = list(new_results.segments[0].analyses.energy.network.keys())
        #print(keys)
        #print(new_results.segments[0].analyses.energy.network[keys[0]].thrust)

        #Need engine chars
        thrust_required[i] = new_results.segments[0].analyses.energy.network[keys[0]].thrust.outputs.thrust
        tsfc[i] = new_results.segments[0].analyses.energy.network[keys[0]].thrust.outputs.thrust_specific_fuel_consumption
        specific_impulse[i] = new_results.segments[0].analyses.energy.network[keys[0]].thrust.outputs.specific_impulse
        throttle[i]         = new_results.segments[0].conditions.propulsion.throttle[:,0]


        if verbose:
            print('Iteration: ', i)

        #print(breakdown)

        analyses = copy.deepcopy(place_holder)
        #End of loop


    


    return [aoa, drag, lift, speed, mach, temp, pres, dynamic_pres, stag_temp, stag_pres, thrust_required, tsfc, specific_impulse, throttle]


