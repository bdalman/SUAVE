## @ingroup Input_Output-CONSOLE
# make_a_folder.py
#
# Created:  Aug 2019, B. Dalman

import subprocess

## @ingroup Input_Output-CONSOLE
def make_a_folder(tag):
    """This calls the console to make a new folder in the current working directory

    Assumptions:
    new folder will be created that hopefully doesn't already exist

    Source:
    N/A

    Inputs:
    tag        <string>  This corresponds to a configuration from SUAVE

    Outputs:
    the folder you want

    Properties Used:
    N/A
    """          
                              
    # Call as would be done in the terminal
    subprocess.call(['mkdir',tag])
    
    pass