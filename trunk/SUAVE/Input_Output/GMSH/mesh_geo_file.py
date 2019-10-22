## @ingroup Input_Output-GMSH
# mesh_geo_file.py
#
# Created:  Oct 2016, T. MacDonald
# Modified: Jan 2017, T. MacDonald

import subprocess
import os
import re



_EXEC_ENV_REMOVE = re.compile('^(OMPI|PMIX)')

## @ingroup Input_Output-GMSH
def mesh_geo_file(tag):
    """This calls GMSH to create a volume mesh based on a previously created .geo file.
    The volume mesh can be read by SU2.

    Assumptions:
    .geo file created with write_geo_file function in this folder

    Source:
    N/A

    Inputs:
    tag        <string>  This corresponds to a configuration from SUAVE

    Outputs:
    <tag>.su2  This is a mesh file in SU2 format

    Properties Used:
    N/A
    """          
    if os.path.isfile(tag+'.su2') == True:
        os.remove(tag+'.su2') # This prevents an leftover mesh from being used when SU2 is called
                              # This is important because otherwise the code will continue even if gmsh fails

    print('Tag being used for gmsh process is: ', tag)


    f = open('mesh_log_file.txt', 'a')
    f.write('# ----- Writing new mesh output! ----- #')
    f.write('\n')
                              
    # Call Gmsh as would be done in the terminal
    subprocess.run(['gmsh',tag+'.geo','-3','-o',tag+'.su2','-format','su2', '-saveall', '-v', '5', '-cpu'], stdout=f, stderr=subprocess.STDOUT, env=_safe_env())

    f.close()

    print('Finished gmsh subprocess!')
    
    pass

def _safe_env():
    return dict(
        [(k,v) for k, v in os.environ.items() if not _EXEC_ENV_REMOVE.search(k)],
    )