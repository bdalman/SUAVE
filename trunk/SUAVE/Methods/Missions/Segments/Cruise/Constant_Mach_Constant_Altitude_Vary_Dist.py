## @ingroup Methods-Missions-Segments-Cruise
# Constant_Mach_Constant_Altitude_Vary_Dist.py
# 
# Created:  Jul 2014, SUAVE Team
# Modified: Jan 2016, E. Botero
# Modified: Apr 2019, B. Dalman

# --------------------------------------------------------------
# Imports
# --------------------------------------------------------------

import SUAVE
import numpy as np


# This script to vary cruise distance until it reaches a set final cruise weight

# --------------------------------------------------------------
#   Initialize - for cruise distance
# --------------------------------------------------------------
## @ingroup Methods-Missions-Segments-Cruise
def initialize_cruise_distance(segment):
    """This is a method that allows your vehicle to land at prescribed landing weight

    Assumptions:
    N/A

    Source:
    N/A

    Inputs:
    segment.cruise_tag              [string]
    segment.distance                [meters]

    Outputs:
    state.unknowns.cruise_distance  [meters]

    Properties Used:
    N/A
    """         

    # unpack
    cruise_tag = segment.cruise_tag
    #p_0         = segment.stagnation_pressure
    #q           = segment.dynamic_pressure
    alt         = segment.altitude 
    t_nondim    = segment.state.numerics.dimensionless.control_points
    conditions  = segment.state.conditions
    mach        = segment.mach

    # Unpack Unknowns
    throttle   = segment.state.unknowns.throttle
    theta      = segment.state.unknowns.body_angle
    cruise_distance   = segment.state.unknowns.distance[-1]


    SUAVE.Methods.Missions.Segments.Common.Aerodynamics.update_atmosphere(segment) 
    a = conditions.freestream.speed_of_sound[:,0]

    v_mag = np.multiply(mach,a)

    # check for initial altitude
    if alt is None:
        if not segment.state.initials: raise AttributeError('altitude not set')
        alt = -1.0 * segment.state.initials.conditions.frames.inertial.position_vector[-1,2]
        segment.altitude = alt



    t_initial = conditions.frames.inertial.time[0,0]
    t_final      = cruise_distance / v_mag + t_initial

    time = t_nondim * (t_final  -t_initial) + t_initial

    #mass_initial = segment.state.conditions.total_mass[0]


    segment.state.conditions.freestream.altitude[:,0]             = alt
    segment.state.conditions.frames.inertial.position_vector[:,2] = -alt # z points down
    segment.state.conditions.frames.inertial.velocity_vector[:,0] = v_mag
    segment.state.conditions.frames.inertial.time[:,0]            = time[:,0]
    
    
    # apply, make a good first guess
    segment.state.unknowns.cruise_distance = cruise_distance
    
    return


# --------------------------------------------------------------
#   Unknowns - for cruise distance
# --------------------------------------------------------------

## @ingroup Methods-Missions-Segments-Cruise
def unknown_cruise_distance(segment):
    """This is a method that allows your vehicle to land at prescribed landing weight

    Assumptions:
    N/A

    Source:
    N/A

    Inputs:
    segment.cruise_tag              [string]
    state.unknowns.cruise_distance  [meters]

    Outputs:
    segment.distance                [meters]

    Properties Used:
    N/A
    """      
    
    # unpack
    distance = segment.state.unknowns.cruise_distance
    cruise_tag = segment.cruise_tag
    

    #print('Distance in unknown_cruise_distance: ', segment.state.unknowns)
    # apply the unknown
    segment.distance = distance
    
    return


# --------------------------------------------------------------
#   Residuals - for Take Off Weight
# --------------------------------------------------------------

## @ingroup Methods-Missions-Segments-Cruise
def residual_landing_weight(segment):
    """This is a method that allows your vehicle to land at prescribed landing weight.
    This takes the final weight and compares it against the prescribed landing weight.

    Assumptions:
    N/A

    Source:
    N/A

    Inputs:
    segment.state.segments[-1].conditions.weights.total_mass [kilogram]
    segment.target_landing_weight                            [kilogram]

    Outputs:
    segment.state.residuals.landing_weight                   [kilogram]

    Properties Used:
    N/A
    """      
    
    # unpack
    landing_weight = segment.state.conditions.weights.total_mass[-1]
    target_weight  = segment.target_landing_weight
    
    # this needs to go to zero for the solver to complete
    segment.state.residuals.landing_weight = landing_weight - target_weight
    
    return
    
def update_differentials(segment):
    """ On each iteration creates the differentials and integration functions from knowns about the problem. Sets the time at each point. Must return in dimensional time, with t[0] = 0. This is different from the common method as it also includes the scaling of operators.

        Assumptions:
        Works with a segment discretized in vertical position, altitude

        Inputs:
        state.numerics.dimensionless.control_points      [Unitless]
        state.numerics.dimensionless.differentiate       [Unitless]
        state.numerics.dimensionless.integrate           [Unitless]
        state.conditions.frames.inertial.position_vector [meter]
        state.conditions.frames.inertial.velocity_vector [meter/second]
        

        Outputs:
        state.conditions.frames.inertial.time            [second]

    """    

    # unpack
    numerics   = segment.state.numerics
    conditions = segment.state.conditions
    x    = numerics.dimensionless.control_points
    D    = numerics.dimensionless.differentiate
    I    = numerics.dimensionless.integrate 
    r    = segment.state.conditions.frames.inertial.position_vector[:,0]
    v    = segment.state.conditions.frames.inertial.velocity_vector
    start= r[0]
    end  = r[-1]   

    dx = end - start
    #vz = -v[:,2,None] # maintain column array
    vx = v[:,0] 

    # get overall time step
    dt = (dx/np.dot(I[-1,:],vx))

    
    print('Diffs: ', dt, I, vx)

    # Calculate the positions
    posn = np.dot(I*dt,vx) + start


    # rescale operators
    x = x * dt
    D = D / dt
    I = I * dt
    


    

    # pack
    t_initial                                       = segment.state.conditions.frames.inertial.time[0,0]

    numerics.time.control_points                    = x
    numerics.time.differentiate                     = D
    numerics.time.integrate                         = I
    conditions.frames.inertial.time[1:,0]            = t_initial + x[1:,0] 
    conditions.frames.inertial.position_vector[:,0] = r 
    #conditions.freestream.altitude[:,0]             =  alt[:,0] # positive altitude in this context    

    return