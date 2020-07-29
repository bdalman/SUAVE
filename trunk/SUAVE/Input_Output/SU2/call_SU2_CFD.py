## @ingroup Input_Output-SU2
# call_SU2_CFD.py
# 
# Created:  Oct 2016, T. MacDonald
# Modified: Jan 2017, T. MacDonald
#           Mar 2018, T. MacDonald

import subprocess
from SUAVE.Core import Data
import sys, os
import re


_EXEC_ENV_REMOVE = re.compile('^(OMPI|PMIX)')

## @ingroup Input_Output-SU2
def call_SU2_CFD(tag,parallel=False,processors=1):
    """This calls SU2 to perform an analysis according to the related .cfg file.

    Assumptions:
    None

    Source:
    N/A

    Inputs:
    tag                          <string>  This determines what .cfg is used and what the output file is called.
    parallel   (optional)        <boolean> This determines if SU2 will be run in parallel. This setting requires that SU2 has been built to allow this.
    processors (optional)        [-]       The number of processors used for a parallel computation.

    Outputs:
    <tag>_history.dat            This file has the SU2 convergence history.
    CL                           [-]
    CD                           [-]

    Properties Used:
    N/A
    """       
    
    try:
        if parallel==True:
            sys.path.append(os.environ['SU2_HOME'])
            print("Executing SU2 in parallel!")
            from parallel_computation import parallel_computation
            parallel_computation( tag+'.cfg', processors ) # This actually seems to work for parallel
            pass
        else:
            #Old line below
            #subprocess.call(['SU2_CFD',tag+'.cfg'])
            #New process:
            #from parallel_computation import parallel_computation
            #parallel_computation( tag+'.cfg', processors) #Processors here should default to 1
            
            #subprocess.run(['which', 'parallel_computation.py'])
            #subprocess.run(['echo', '$SU2_RUN'])
            #subprocess.run(['echo', 'LINE'])
            #print(sys.path)

            subprocess.run(['SU2_CFD', tag+'.cfg'], env=_safe_env())

            #subprocess.run(['parallel_computation.py','-n',processors,'-f',tag+'.cfg'], stdout=f, stderr=subprocess.STDOUT)
        CFD_FAILED_TO_EXECUTE = False
    except:
        CFD_FAILED_TO_EXECUTE = True

    if not CFD_FAILED_TO_EXECUTE:        
        f = open(tag + '_history.csv')
            
        SU2_results = Data()    
        
        lines = f.readlines()
        final_state = lines[-1].split(',')
        
        # Lift and Drag
        
        CL  = float(final_state[1])
        CD  = float(final_state[2])
        
        SU2_results.coefficient_of_lift  = CL
        SU2_results.coefficient_of_drag  = CD
        
        print('CL:',CL)
        print('CD:',CD)
        
        # Moments
        # Moments are currently not recorded since no
        # reasonable reference length has been chosen
        
        CMx = float(final_state[4])
        CMy = float(final_state[5])
        CMz = float(final_state[6])   
        
        SU2_results.moment_coefficient_x = CMx
        SU2_results.moment_coefficient_y = CMy
        SU2_results.moment_coefficient_z = CMz
        
        print('CMx:',CMx)
        print('CMy:',CMy)
        print('CMz:',CMz)    
                
        return CL,CD, CMy

    else:
        print('Failed to execute CFD, passing back marker values')
        CL = 9999
        CD = 9999
        CMy = 9999
        return CL,CD,CMy

def _safe_env():
    return dict(
        [(k,v) for k, v in os.environ.items() if not _EXEC_ENV_REMOVE.search(k)],
    )

if __name__ == '__main__':
    call_SU2_CFD('cruise',parallel=True)
