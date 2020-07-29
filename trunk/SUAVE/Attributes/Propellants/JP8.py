## @ingroup Attributes-Propellants
# JP8
#
# Created:  July 2020, B. Dalman

# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------
from .Propellant import Propellant

# ----------------------------------------------------------------------
#  JP8 Propellant Class
# ----------------------------------------------------------------------
## @ingroup Attributes-Propellants
class JP8(Propellant):
    """Holds values for this propellant
    
    Assumptions:
    None
    
    Source:
    https://www.ncbi.nlm.nih.gov/books/NBK231234/
    """

    def __defaults__(self):
        """This sets the default values.

        Assumptions:
        None

        Source:
        Values commonly available
        https://www.ncbi.nlm.nih.gov/books/NBK231234/
        & "Performance of JP-8 Unified Fuel in a Small Bore Indirect Injection Diesel Engine for APU Applications", Soloiu, Covington, Lewis, Duggan, LoBue, & Jansons, SAE International 2021

        Inputs:
        None

        Outputs:
        None

        Properties Used:
        None
        """    
        self.tag                        = 'JP8'
        self.reactant                   = 'O2'
        self.density                    = 806.0                          # kg/m^3 (15 C, 1 atm)
        self.specific_energy            = 41.74e6                        # J/kg
        self.energy_density             = 33642.4e6                      # J/m^3
        self.stoichiometric_fuel_to_air = 0.0671            

        # critical temperatures
        self.temperatures.flash        = 311.15                # K
        self.temperatures.autoignition = 502.15                 # This is estimate from atsdr.cdc.gov/ToxProfiles/tp121-c4.pdf
        self.temperatures.freeze       = 226.15                 # K