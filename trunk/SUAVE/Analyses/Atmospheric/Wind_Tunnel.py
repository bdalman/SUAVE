## @ingroup Analyses-Atmospheric
# Wind_Tunnel.py
#
# Created: 
# Modified: June 2020, B. Dalman

# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------

import numpy as np
from warnings import warn

import SUAVE

from SUAVE.Analyses.Atmospheric import Atmospheric

from SUAVE.Attributes.Gases import Air
from SUAVE.Attributes.Planets import Earth

from SUAVE.Analyses.Mission.Segments.Conditions import Conditions

from SUAVE.Core import Units
from SUAVE.Core.Arrays import atleast_2d_col


# ----------------------------------------------------------------------
#  Classes
# ----------------------------------------------------------------------

## @ingroup Analyses-Atmospheric
class Wind_Tunnel(Atmospheric):

    """ Implements the an easily customizable atmospheric model.
    Choose the temperature and pressure for a given test condition, and rho/Re/etc will be calculated from that
    (Re calc happens in Methods-Missions-Segments-Common-Aerodynamics - update_freestream)
        
    Assumptions:
    None
    
    Source:
    None
    """
    
    def __defaults__(self):
        """This sets the default values for the analysis to function.

        Assumptions:
        None

        Source:
        N/A

        Inputs:
        None

        Output:
        None

        Properties Used:
        None
        """     
        
        atmo_data = SUAVE.Attributes.Atmospheres.Earth.Wind_Tunnel()
        self.update(atmo_data)        
    
    def compute_values(self,altitude,temperature_deviation=0.0,var_gamma=False):

        """Computes atmospheric values.

        Assumptions:
        None

        Source:
        None

        Inputs:
        altitude                                 [m]
        temperature_deviation                    [K]

        Output:
        atmo_data.
          pressure                               [Pa]
          temperature                            [K]
          speed_of_sound                         [m/s]
          dynamic_viscosity                      [kg/(m*s)]

        Properties Used:
        self.
          fluid_properties.gas_specific_constant [J/(kg*K)]
          planet.sea_level_gravity               [m/s^2]
          planet.mean_radius                     [m]
          breaks.
            altitude                             [m]
            temperature                          [K]
            pressure                             [Pa]
        """

        # unpack
        zs        = altitude
        gas       = self.fluid_properties
        planet    = self.planet
        grav      = self.planet.sea_level_gravity        
        Rad       = self.planet.mean_radius
        R         = gas.gas_specific_constant
        delta_isa = temperature_deviation

        # check properties
        if not gas == Air():
            warn('Wind Tunnel not using Air fluid properties')
        if not planet == Earth():
            warn('Wind Tunnel not using Earth planet properties')          
        
        # convert input if necessary
        zs = atleast_2d_col(zs)


        # initialize return data
        ones = np.ones_like(zs)
        p     = ones * 1.0
        T     = ones * 1.0
       
       
        # Calculate freestream properties 
        T   = T * self.temperature
        p   = p * self.pressure
        rho = gas.compute_density(T,p)
        a   = gas.compute_speed_of_sound(T,p,var_gamma)
        mu  = gas.compute_absolute_viscosity(T)
                
        atmo_data = Conditions()
        atmo_data.expand_rows(zs.shape[0])
        atmo_data.pressure          = p
        atmo_data.temperature       = T
        atmo_data.density           = rho
        atmo_data.speed_of_sound    = a
        atmo_data.dynamic_viscosity = mu
        
        return atmo_data


# ----------------------------------------------------------------------
#   Module Tests
# ----------------------------------------------------------------------
if __name__ == '__main__':
    
    # import pylab as plt
    
    # h = np.linspace(-1.,60.,200) * Units.km
    # delta_isa = 0.
    # h = 5000.
    # atmosphere = US_Standard_1976()
    
    # data = atmosphere.compute_values(h,delta_isa)
    # p   = data.pressure
    # T   = data.temperature
    # rho = data.density
    # a   = data.speed_of_sound
    # mu = data.dynamic_viscosity
    
    #print(data)
    print('Need to write test for Wind_Tunnel Analyses Class!')
    