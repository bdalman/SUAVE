## @ingroup Methods-Performance
# size_mission_accel_for_aoa.py
#
# Created:  June 2019, B. Dalman

# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------

import numpy as np

# ----------------------------------------------------------------------
#  Calculate the range of  Payload Range Diagram
# ----------------------------------------------------------------------

## @ingroup Methods-Performance
def size_mission_accel_for_aoa(mission,target_aoas):
    """Given a mission series with single points, and target AoAs, this function recalculates accels of the single points to achieve the target AoAs

    Assumptions:
    A series of single point mission segments for AoA sweep
    Single point missions are named sequentially, starting with 'single_point_1'

    Source:
    N/A

    Inputs:
        mission
            single_point_segments
            segments.z_accel              [m/s^2]
        target_aoas                       [deg]
    
    Outputs:
        results (using new_z_accels)

    Properties Used:
    N/A

    """   
    #unpack
    target_AOA          = target_aoas
    num_sections        = len(target_AOA)
    


    #Declare new arrays for later
    actual_AOA        = np.zeros(num_sections)
    resid_AOA         = np.zeros(num_sections)
    old_z_accels      = np.zeros(num_sections)
    delta_z_accels    = np.zeros(num_sections)
    new_z_accels      = np.zeros(num_sections)

    #Variables to be used later
    tol      = 0.001
    iteration = 0
    maxIter   = 50
    tag                 = 'single_point_'
    

    print('About to evaluate mission for AOAs')
    results = mission.evaluate()

    #This loop fills the zero arrays just declared
    for i in range(0, num_sections):
        segment_tag = tag + str(i+1)

        actual_AOA[i] = results.segments[segment_tag].conditions.aerodynamics.angle_of_attack
        old_z_accels[i]     = mission.segments[segment_tag].z_accel



    actual_AOA = actual_AOA * 180 / np.pi   #Convert from rads to decimal
    resid_AOA = target_AOA - actual_AOA 

    #Check to see if converged already
    if np.max(np.absolute(resid_AOA)) < tol:
        print('Segment AOAs are converged!')
        return results


    #If not, loop until it is or it hits max iterations

    while np.max(np.absolute(resid_AOA)) > tol and iteration < maxIter:

        for i in range(0,num_sections):  
            if old_z_accels[i]==0:
                delta_z_accels[i] = resid_AOA[i] * (-10)
            elif old_z_accels[i]<0:
                #Actual is higher than target, so the z-accel is too high upwards (but z-coord points down, so the number is negative and needs to get closer to zero)

                delta_z_accels[i] = old_z_accels[i] * resid_AOA[i] * (0.35/np.log(np.absolute(old_z_accels[i])))  #old_z_accel is always (-), so positive resid will push z_accel down, negative resid (actual higher than target) pushes z_accel up

            elif old_z_accels[i]>0:
                #Actual is lower than target
                delta_z_accels[i] = old_z_accels[i] * resid_AOA[i] * (-0.35/np.log(np.absolute(old_z_accels[i])))  #resid is always (+) here, so -0.3 means delta will push towards 
            #else: #for old_z ==0
            #    delta_z_accels[i] = resid_AOA[i] * (0.05)

            if target_AOA[i]==0: # This helps convergence if target = 0AoA
                delta_z_accels[i] = resid_AOA[i] * -5


        new_z_accels = old_z_accels + delta_z_accels

        for i in range(0, num_sections):
            segment_tag = tag + str(i+1)

            mission.segments[segment_tag].z_accel = new_z_accels[i]

        #Re-evaluate the mission
        results = mission.evaluate()

        #Fill in the AoAs with the new data
        for i in range(0, num_sections):
            segment_tag = tag + str(i+1)

            actual_AOA[i] = results.segments[segment_tag].conditions.aerodynamics.angle_of_attack
            old_z_accels[i]     = mission.segments[segment_tag].z_accel



        actual_AOA = actual_AOA * 180 / np.pi   #Convert from rads to decimal
        resid_AOA = target_AOA - actual_AOA 

        print('For iteration ', iteration, ' we have max residual of: ', np.max(np.absolute(resid_AOA)))
        #print('Delta_z are: ', delta_z_accels)
        #print('Old_z are: ', old_z_accels)

        iteration += 1

        #Check to see if converged already
        if np.max(np.absolute(resid_AOA)) < tol:
            print('Segment AOAs are converged!')
            return results
        elif iteration >=maxIter:
            print('Max iterations reached!')
            return results


