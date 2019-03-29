## @ingroup Analyses-Energy
# Steady_Flight.py
#
# Created:  
# Modified: Mar 2019, B. Dalman

# For flying analyses with no propulsor

# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------

from SUAVE.Analyses import Analysis


# ----------------------------------------------------------------------
#  Analysis
# ----------------------------------------------------------------------

## @ingroup Analyses-Energy
class Steady_Flight(Analysis):
    """ SUAVE.Analyses.Energy.Steady_Flight()
    """
    def __defaults__(self):
        """This sets the default values and methods for the analysis.
            
                    Assumptions:
                    None
            
                    Source:
                    N/A
            
                    Inputs:
                    None
            
                    Outputs:
                    None
            
                    Properties Used:
                    N/A
                """        
        self.tag     = 'steady_flight'
        self.network = None
        
    def evaluate_thrust(self,state):
        
        """Evaluate the thrust produced by the energy network.
    
                Assumptions:
                Thrust produced is equal to drag calculated - for steady flight calculations
    
                Source:
                N/A
    
                Inputs:
                State data container - Drag
    
                Outputs:
                A thrust value
    
                Properties Used:
                N/A                
            """
                
            
        forces = state.conditions.frames.inertial.total_force_vector
        drag = abs(forces[0])
        results = network.evaluate_thrust(state) 
        
        return results
    