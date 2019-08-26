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


def mach_and_alt_sweep(analyses, mach_targets, alt_targets):
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
    target_alts = alt_targets


    num_sections = len(target_speeds)
    num_alts = len(target_alts)

    print('Passed in target speeds: ', target_speeds)
    print('Passed in target alts: ', target_alts)


    # Initialize results variables you care about for plotting

    aoa = np.zeros(num_sections * num_alts)
    drag = np.zeros(num_sections * num_alts)
    lift = np.zeros(num_sections * num_alts)
    speed = np.zeros(num_sections * num_alts)
    mach = np.zeros(num_sections * num_alts)
    alt = np.zeros(num_sections * num_alts)
    temp = np.zeros(num_sections * num_alts)
    pres = np.zeros(num_sections * num_alts)
    dynamic_pres = np.zeros(num_sections * num_alts)
    stag_temp = np.zeros(num_sections * num_alts)
    stag_pres = np.zeros(num_sections * num_alts)

    thrust_required = np.zeros(num_sections * num_alts)
    tsfc = np.zeros(num_sections * num_alts)
    specific_impulse = np.zeros(num_sections * num_alts)

    total_count = 0

    for j in range(0, num_alts):
        for i in range(0, num_sections):
            analyses.missions.base.segments[0].air_speed = target_speeds[i]
            analyses.missions.base.segments[0].altitude = target_alts[j]
            analyses.finalize()

            mission = analyses.missions.base

            new_results = mission.evaluate()

            #print(new_results.segments[0].conditions.freestream.keys())

            #Plane chars to save

            
            aoa[total_count] = new_results.segments[0].conditions.aerodynamics.angle_of_attack
            drag[total_count] = -1 * new_results.segments[0].conditions.frames.wind.drag_force_vector[:,0]
            lift[total_count] = -1 * new_results.segments[0].conditions.frames.wind.lift_force_vector[:,2]
            speed[total_count] = target_speeds[i]
            mach[total_count] = new_results.segments[0].conditions.freestream.mach_number
            alt[total_count] = target_alts[j]
            temp[total_count] = new_results.segments[0].conditions.freestream.temperature
            pres[total_count] = new_results.segments[0].conditions.freestream.pressure
            dynamic_pres[total_count] = new_results.segments[0].conditions.freestream.dynamic_pressure
            stag_temp[total_count] = new_results.segments[0].conditions.freestream.stagnation_temperature
            stag_pres[total_count] = new_results.segments[0].conditions.freestream.stagnation_pressure

            print('For speed of :', new_results.segments[0].conditions.freestream.mach_number)
            print('Lift coef is: ', new_results.segments[0].conditions.aerodynamics.lift_coefficient)
            print('Throttle is: ', new_results.segments[0].state.unknowns.throttle)


            #print(new_results.segments[0].conditions.aerodynamics.drag_breakdown)
            #print(new_results.segments[0].conditions.aerodynamics.lift_coefficient)
            #if i==1:
            #    print(breakdown)

            keys = list(new_results.segments[0].analyses.energy.network.keys())

            
            #print(breakdown)
            #print(keys)
            #print(new_results.segments[0].analyses.energy.network[keys[0]].thrust)

            #Need engine chars
            thrust_required[total_count] = new_results.segments[0].analyses.energy.network[keys[0]].thrust.outputs.thrust
            tsfc[total_count] = new_results.segments[0].analyses.energy.network[keys[0]].thrust.outputs.thrust_specific_fuel_consumption
            specific_impulse[total_count] = new_results.segments[0].analyses.energy.network[keys[0]].thrust.outputs.specific_impulse

            print('Iteration: ', total_count)

            #print(breakdown)

            analyses = copy.deepcopy(place_holder)

            total_count += 1
            #End of loop


    


    return [aoa, drag, lift, speed, mach, alt, temp, pres, dynamic_pres, stag_temp, stag_pres, thrust_required, tsfc, specific_impulse]


