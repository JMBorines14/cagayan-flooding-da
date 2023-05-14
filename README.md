# Cagayan Flooding Simulation

This is the project repository for the CS 198/199 Project entitled *"Creating a Data Analytics Platform to simulate Typhoon Ulysses Flooding in Cagayan Valley"*. This repository contains the Python scripts that were used to generate the *CDFNET4* file containing the projected water depths of the Cagayan Valley during the onslaught of Typhoon Ulysses (November 2020) using a Cellular Automata model.

This repository was made by: <br/>
James Matthew G. Borines <br/>
Alyssa Beatrice A. Diokno
<hr/>

## Before Running the Script
This simulation script uses third-library Python libraries, which were installed using `pip`. Before running the Python scripts, the following third-party Python libraries must be installed on your local machine:
1. **netCDF4**: To install netCDF4 Python library on your local machine, you may refer to this [LINK](https://unidata.github.io/netcdf4-python/#quick-install).
2. **gdal**: To install the GDAL Python library on your local machine, you may refer to this [LINK](https://opensourceoptions.com/blog/how-to-install-gdal-for-python-with-pip-on-windows/). 
3. **numpy**: To install numpy on your local machine, you may refer to this [LINK](https://numpy.org/install/).

You may type the following command at your terminal/command prompt:
```
pip install numpy netCDF4
```
The `gdal` library requires a special installation that does not follow the conventional installation (as shown in the command above). Make sure to follow the instructions stated in the link above. 
<hr/>

## Running the Script
Only the `main.py` script must be run to generate the output files. The remaining Python files (`camodel.py` and `rainfall.py`) contain the necessary auxiliary functions for the simulation, and are imported to `main.py`. To produce the output of this simulation, one can enter the following command at the terminal/command prompt:
```
python main.py path_to_tif_input_file.tif
```
where `path_to_tif_input_file` indicates the current path of the TIF file input. Once the script finishes, a `output_dataset.nc` must be present at your current working directory. 