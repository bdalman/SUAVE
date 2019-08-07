# -User defined: bank angle, start and end direction?
#
#
#
#
#
#

## @ingroup Analyses-Mission-Segments-Cruise
# Constant_Bank_Angle_Constant_Altitude.py
# 
# Created:  June 2019, B. Dalman


# -------------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------------

from SUAVE.Analyses.Mission.Segments import Aerodynamic
from SUAVE.Analyses.Mission.Segments import Conditions

from SUAVE.Methods.Missions import Segments as Methods

from SUAVE.Analyses import Process

# Units
from SUAVE.Core import Units

## Segment

class Constant_Bank_Angle_Constant_Altitude(Aerodynamic):
	""" Vehicle flies at a constant pitch rate at a set altitude. This is maneuvering flight.
        This is used in VTOL aircraft which need to transition from one pitch attitude to another.
    
        Assumptions:
        None
        
        Source:
        None
    """ 

    def __defaults__(self):
    	""" This sets the default solver flow. Anything in here can be modified after initializing a segment.
    
            Assumptions:
            Constant air speed
            Always starts in the same direction?? Does this make a difference? Not if it's low fidelity and earth curvature and accurate wind isn't included I don't think
            Level turn (no z-accel)
    
            Source:
            N/A
    
            Inputs:
            Bank angle (is it bank or roll angle??) or turning radius
            End direction or total distance?
            Airspeed
            Altitude
    
            Outputs:
            None
    
            Properties Used:
            None
        """  

		# -------------------------------------------------------------------------
		# User inputs
		# -------------------------------------------------------------------------
		self.altitude  		= None
        self.air_speed 		= 10. * Units['km/hr']
        self.distance  		= 10. * Units.km #Total circumferential distance
        self.bank_angle 	= 15 * Units.degrees # Or roll angle? Check Anderson
        self.turn_rate 		= 0.5 * Units['deg/s']

        #self.end_direction  = #not sure what unit this should even have??


		# -------------------------------------------------------------------------
		# Mission Unknowns
		# -------------------------------------------------------------------------

		# Import conditions
		self.state.conditions.update( Conditions.Aerodynamics() )

		#Thottle, body angle,
		ones_row = self.state.ones_row
		self.state.unknowns.throttle = ones_row(1) * 0.8
		self.state.unknowns.body_angle = ones_row(1) * 1.0 * Units.deg
		#self.state.unknowns.yaw_angle = ones_row(1) * 0.5 * Units.deg


		# Residuals
		self.state.residuals.forces = ones_row(3) * 0.0 #Need 3 forces for the turning case
		# Lcos(roll_angle) = W  ---> z_dir (assumes no yaw, thrust acts straight down x)
		# Lsin(roll_angle) = m * v^2/radius_of_curve ---> y-dir
		# T = D ---> x_dir (assumes no yaw again)



		# -------------------------------------------------------------------------
		# Initialize
		# -------------------------------------------------------------------------

		initialize = self.process.initialize

		initialize.expand_state 		= Methods.expand_state   #SUAVE.Methods.Missions.Segments.expand_state

		# I think this is the step that determines the 
		initialize.differentials 		= Methods.Common.Numerics.initialize_differentials_dimensionless #SUAVE.Methods.Missions.Segments.Common.Numerics.i_d_d
		initialize.conditions 			= Methods.Cruise.Constant_Bank_Angle_Constant_Altitude.initialize_conditions # TODO


		# -------------------------------------------------------------------------
		# Convergence Method & Functions for iteration
		# -------------------------------------------------------------------------

		converge = self.process.converge

		converge.converge_root 			= Methods.converge_root #SUAVE.Methods.Missions.Segments.converge_root


		# --------------------------------------------------------------
        #   Iterate - this is iterated
        # --------------------------------------------------------------
        iterate = self.process.iterate

        #Update initials
        iterate.initials = Process()
        iterate.initials.time 				= Methods.Common.Frames.initialize_time #SUAVE.Methods.Missions.Segments.Common.Frames.init_time
        iterate.initials.weights 			= Methods.Common.Weights.initialize_weights #SUAVE.Methods.Missions.Segments.Common.Weights.initialize_weights
        iterate.initials.inertial_position 	= Methods.Common.Frames.initialize_inertial_position #REMAKE for 3D??
        iterate.initials.planet_position 	= Methods.Common.Frames.initialize_planet_position #REMAKE for 3D??

        #Unpack unknowns
        iterate.unknowns = Process()
        iterate.unknowns.mission 			= Methods.Cruise.Common.unpack_unknowns #Can use??
        #iterate.unknowns.mission 			 = Methods.Cruise.Constant_Bank_Angle_Constant_Altitude.unpack_unknowns    #TODO Alternative

        #Update conditions
        iterate.conditions = Process()
        iterate.conditions.differentials 	= Methods.Common.Numerics.update_differentials_time
        iterate.conditions.altitude 		= Methods.Common.Aerodynamics.update_altitude
        iterate.conditions.atmosphere 		= Methods.Common.Aerodynamics.update_atmosphere
        iterate.conditions.gravity         = Methods.Common.Weights.update_gravity
        iterate.conditions.freestream      = Methods.Common.Aerodynamics.update_freestream #REMAKE
        iterate.conditions.orientations    = Methods.Common.Frames.update_orientations #REMAKE
        iterate.conditions.aerodynamics    = Methods.Common.Aerodynamics.update_aerodynamics #REMAKE
        iterate.conditions.stability       = Methods.Common.Aerodynamics.update_stability #REMAKE
        iterate.conditions.propulsion      = Methods.Common.Energy.update_thrust #REMAKE??
        iterate.conditions.weights         = Methods.Common.Weights.update_weights
        iterate.conditions.forces          = Methods.Common.Frames.update_forces #REMAKE
        iterate.conditions.planet_position = Methods.Common.Frames.update_planet_position #REMAKE

        #Solve residuals
        iterate.residuals = Process()
        iterate.residuals.total_forces 		= Methods.Cruise.Common.residual_total_forces #REMAKE
        #iterate.residuals.total_forces 		= Methods.Cruise.Constant_Bank_Angle_Constant_Altitude.residual_total_forces #TODO Alternative



		# -------------------------------------------------------------------------
		# Finalize & Outputs
		# -------------------------------------------------------------------------

		finalize = self.process.finalize

		#Post process
		finalize.post_process = Process()
		finalize.post_process.inertial_position = Methods.Common.Frames.integrate_inertial_horizontal_position #REMAKE or add different calc method for extra dimension?
		finalize.post_process.stability 		= Methods.Common.Aerodynamics.update_stability

		return



