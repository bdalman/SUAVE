## @ingroup Methods-Performance
# size_mission_accel_for_cl.py
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
def size_mission_accel_for_cl(mission,target_CLs):
    """Given a mission series with single points, and target CLs, this function recalculates accels of the single points to achieve the target CLs

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
    target_cl          = target_CLs
    num_sections        = len(target_cl)
    


    #Declare new arrays for later
    actual_cl        = np.zeros(num_sections)
    resid_cl         = np.zeros(num_sections)
    old_z_accels      = np.zeros(num_sections)
    delta_z_accels    = np.zeros(num_sections)
    new_z_accels      = np.zeros(num_sections)
    first_z_accels    = np.zeros(num_sections)

    #Variables to be used later
    tol      = 0.005
    iteration = 0
    maxIter   = 50
    tag                 = 'single_point_'


    print('About to evaluate mission for CLs')
    results = mission.evaluate()

    #This loop fills the zero arrays just declared
    for i in range(0, num_sections):
        segment_tag = tag + str(i+1)

        actual_cl[i] = results.segments[segment_tag].conditions.aerodynamics.lift_coefficient
        old_z_accels[i]     = mission.segments[segment_tag].z_accel


    first_z_accels = old_z_accels

    actual_cl = actual_cl * 180 / np.pi   #Convert from rads to decimal
    resid_cl = target_cl - actual_cl 

    #Check to see if converged already
    if np.max(np.absolute(resid_cl)) < tol:
        print('Segment CLs are converged!')
        return results


    #If not, loop until it is or it hits max iterations

    while np.max(np.absolute(resid_cl)) > tol and iteration < maxIter:


        #print('CLs (act): ', actual_cl, 'target: ', target_cl, 'resid', resid_cl)#, old_z_accels[0], delta_z_accels[0])

        for i in range(0,num_sections):  
            if old_z_accels[i]==0:
                delta_z_accels[i] = resid_cl[i] * (-10)
            elif old_z_accels[i]<0:
                #Actual is higher than target, so the z-accel is too high upwards (but z-coord points down, so the number is negative and needs to get closer to zero)

                delta_z_accels[i] = old_z_accels[i] * resid_cl[i] * (0.15/np.log(np.absolute(old_z_accels[i]))) #* (first_z_accels[i]**2)/(old_z_accels[i]**2)  #old_z_accel is always (-), so positive resid will push z_accel down, negative resid (actual higher than target) pushes z_accel up

            elif old_z_accels[i]>0:
                #Actual is lower than target
                delta_z_accels[i] = old_z_accels[i] * resid_cl[i] * (-0.15/np.log(np.absolute(old_z_accels[i]))) #* (first_z_accels[i]**2)/(old_z_accels[i]**2)  #resid is always (+) here, so -0.3 means delta will push towards 
            #else: #for old_z ==0
            #    delta_z_accels[i] = resid_AOA[i] * (0.05)

            if target_cl[i]==0: # This helps convergence if target = 0AoA
                delta_z_accels[i] = resid_cl[i] * -5


        new_z_accels = old_z_accels + delta_z_accels

        for i in range(0, num_sections):
            segment_tag = tag + str(i+1)

            mission.segments[segment_tag].z_accel = new_z_accels[i]

        #Re-evaluate the mission
        results = mission.evaluate()

        #Fill in the CLs with the new data
        for i in range(0, num_sections):
            segment_tag = tag + str(i+1)

            actual_cl[i] = results.segments[segment_tag].conditions.aerodynamics.lift_coefficient
            old_z_accels[i]     = mission.segments[segment_tag].z_accel



        actual_cl = actual_cl * 180 / np.pi   #Convert from rads to decimal
        resid_cl = target_cl - actual_cl 

        

        #print('Accels: ', new_z_accels)


        print('For iteration ', iteration, ' we have max residual of: ', np.max(np.absolute(resid_cl)))#np.max(np.absolute(resid_AOA)))
        #print('Delta_z are: ', delta_z_accels)
        #print('Old_z are: ', old_z_accels)

        iteration += 1

        #Check to see if converged already
        if np.max(np.absolute(resid_cl)) < tol:
            print('Segment CLs are converged!')
            return results, resid_cl
        elif iteration >=maxIter:
            print('Max iterations reached!')
            return results, resid_cl


