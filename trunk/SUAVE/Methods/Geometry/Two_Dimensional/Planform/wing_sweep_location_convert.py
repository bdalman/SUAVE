## @ingroup Methods-Geometry-Two_Dimensional-Cross_Section-Planform
# wing_sweep_location_convert.py
#
# Created:  Mar 2020, B. Dalman


# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------

from math import pi
import numpy as np

# ----------------------------------------------------------------------
#  Methods
# ----------------------------------------------------------------------

## @ingroup Methods-Geometry-Two_Dimensional-Cross_Section-Planform
def wing_sweep_location_convert(n, m, sweep_m, A, taper):
    """Takes input of wing sweep at a given chord % m, and converts it to sweep at chord % n

    Assumptions:
    Simple, tapered wing

    Source:
    https://www.fzt.haw-hamburg.de/pers/Scholz/HOOU/AircraftDesign_7_WingDesign.pdf

    Inputs:
    wing
      n - chord location desired for sweep [%]
      m - chord location of current sweep [%]
      sweep_m - sweep angle [deg]
      A - aspect ratio of wing
      taper - taper ratio of wing



    Outputs:
    sweep_n - wing sweep angle at chord location n

    Properties Used:
    N/A
    """     

    sweep_m_rad = sweep_m * pi/180
    sweep_n_rad = np.arctan(np.tan(sweep_m_rad) - (4/A)*( (n-m) * (1-taper)/(1+taper) ) )
    sweep_n = sweep_n_rad * 180/pi   
    
    
    return sweep_n
