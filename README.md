# Get Files From Rede
checks which datafiles are in internal rede ('Z:'), for each cil. can be personalized, shows dates available, cils, management, tt, and can write to an excel file with conditional formatting.  

Download Exe File: https://github.com/FranMacedo/GetFilesFromInternalNetwork/blob/master/run_gui.exe
## Requirements
A connection to rede (Z:) should be available.

## Setup
only if eventual goes to git:
  ```
    git clone
    cd files_from_rede
    py -m venv venv
    venv/scripts/activate
    pip install -r requirements.txt
  ```
  
## Run
-  Run file ```run_gui.bat``` to get info through simple GUI, with personalized query.
-  Run file ```run.bat``` to do exactly the same thing.
-  Run file ```run.py``` to do exactly the same thing, but with no GUI, only cmd user input actions.

- Edit file ```files.py``` to change any query function you wish.


