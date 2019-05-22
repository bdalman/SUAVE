## @ingroup Methods-Missions-Segments-Climb
# Constant_Stagnation_Pressure_Constant_Angle.py
# 
# Created:  Apr 2019, B. Dalman
# Modified from original: C_Q_C_A (Jun 2017, E. Botero)
# Modified:          

# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------
import numpy as np
import SUAVE

# ----------------------------------------------------------------------
#  Initialize Conditions
# ----------------------------------------------------------------------

## @ingroup Methods-Missions-Segments-Climb
def initialize_conditions_unpack_unknowns(segment):
    """Sets the specified conditions which are given for the segment type.

    Assumptions:
    Constrant stagnation pressure and constant rate of climb

    Source:
    N/A

    Inputs:
    segment.climb_angle                                 [radians]
    segment.stagnation_pressure                            [pascals]
    segment.altitude_start                              [meters]
    segment.altitude_end                                [meters]
    segment.state.numerics.dimensionless.control_points [unitless]
    conditions.freestream.density                       [kilograms/meter^3]
    segment.state.unknowns.throttle                     [unitless]
    segment.state.unknowns.body_angle                   [radians]
    segment.state.unknowns.altitudes                    [meter]

    Outputs:
    conditions.frames.inertial.velocity_vector  [meters/second]
    conditions.frames.inertial.position_vector  [meters]
    conditions.propulsion.throttle              [unitless]
    conditions.frames.body.inertial_rotations   [radians]

    Properties Used:
    N/A
    """           
    
    # unpack
    climb_angle = segment.climb_angle
    p_0         = segment.stagnation_pressure
    q           = segment.dynamic_pressure
    alt0        = segment.altitude_start 
    altf        = segment.altitude_end
    t_nondim    = segment.state.numerics.dimensionless.control_points
    conditions  = segment.state.conditions
    rho         = conditions.freestream.density[:,0]
    
    # unpack unknowns
    throttle = segment.state.unknowns.throttle
    theta    = segment.state.unknowns.body_angle
    alts     = segment.state.unknowns.altitudes    

    

    # Update freestream to get density
    SUAVE.Methods.Missions.Segments.Common.Aerodynamics.update_atmosphere(segment)
    rho = conditions.freestream.density[:,0]   

    # check for initial altitude
    if alt0 is None:
        if not segment.state.initials: raise AttributeError('initial altitude not set')
        alt0 = -1.0 * segment.state.initials.conditions.frames.inertial.position_vector[-1,2]
    
    # pack conditions    
    conditions.freestream.altitude[:,0]             =  alts[:,0] # positive altitude in this context    
    
    # Update freestream to get density
    SUAVE.Methods.Missions.Segments.Common.Aerodynamics.update_atmosphere(segment)
    rho = conditions.freestream.density[:,0]       
    
    #Process atmospheric data to get local mach # and velo. This process assumes gamma = 1.4
    p_static = conditions.freestream.pressure[:,0]
    a = conditions.freestream.speed_of_sound[:,0]


    #print('atmospheric are: ', p_static, alts)

    p_r = np.divide(p_0, p_static)
    placeholder = 0.4/1.4

    inside = np.power(p_r,placeholder)

    mach = np.sqrt(5 * ( inside - 1) )
    v_mag = np.multiply(mach,a)

    

    #print('The calculated v is: ', v_mag)

    # Calculate local velo at each point
    #v_mag = 
    # process velocity vector
    #v_mag = np.sqrt(2*q/rho)

    #print('v_mag from mach is: ', v_mag)
    v_x   = v_mag * np.cos(climb_angle)
    v_z   = -v_mag * np.sin(climb_angle)
    
    # pack conditions    
    conditions.frames.inertial.velocity_vector[:,0] = v_x
    conditions.frames.inertial.velocity_vector[:,2] = v_z
    conditions.frames.inertial.position_vector[:,2] = -alts[:,0] # z points down
    conditions.propulsion.throttle[:,0]             = throttle[:,0]
    conditions.frames.body.inertial_rotations[:,1]  = theta[:,0]  
    
## @ingroup Methods-Missions-Segments-Climb
def residual_total_forces(segment):
    """Takes the summation of forces and makes a residual from the accelerations and altitude.

    Assumptions:
    No higher order terms.

    Source:
    N/A

    Inputs:
    segment.state.conditions.frames.inertial.total_force_vector   [Newtons]
    segment.state.conditions.frames.inertial.acceleration_vector  [meter/second^2]
    segment.state.conditions.weights.total_mass                   [kilogram]
    segment.state.conditions.freestream.altitude                  [meter]

    Outputs:
    segment.state.residuals.forces                                [Unitless]

    Properties Used:
    N/A
    """     
    
    # Unpack results
    FT = segment.state.conditions.frames.inertial.total_force_vector
    a  = segment.state.conditions.frames.inertial.acceleration_vector
    m  = segment.state.conditions.weights.total_mass    
    alt_in  = segment.state.unknowns.altitudes[:,0] 
    alt_out = segment.state.conditions.freestream.altitude[:,0] 

    #print('Alts:', alt_in, alt_out)
    
    # Residual in X and Z, as well as a residual on the guess altitude
    segment.state.residuals.forces[:,0] = FT[:,0]/m[:,0] - a[:,0]
    segment.state.residuals.forces[:,1] = FT[:,2]/m[:,0] - a[:,2]
    segment.state.residuals.forces[:,2] = (alt_in - alt_out)/alt_out[-1]

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
    r    = segment.state.conditions.frames.inertial.position_vector
    v    = segment.state.conditions.frames.inertial.velocity_vector
    alt0 = segment.altitude_start
    altf = segment.altitude_end   

    dz = altf - alt0
    vz = -v[:,2,None] # maintain column array

    # get overall time step
    dt = (dz/np.dot(I[-1,:],vz))[-1]

    
    # Calculate the altitudes
    alt = np.dot(I*dt,vz) + alt0


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
    conditions.frames.inertial.position_vector[:,2] = -alt[:,0] # z points down
    conditions.freestream.altitude[:,0]             =  alt[:,0] # positive altitude in this context    

    return