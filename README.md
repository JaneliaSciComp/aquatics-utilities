# aquatics-utilities [![Picture](https://raw.github.com/janelia-flyem/janelia-flyem.github.com/master/images/HHMI_Janelia_Color_Alternate_180x40.png)](http://www.janelia.org)

## Utility programs for Aquatics

These applications process exported AMS data to create new tab-delimited files to be loaded into PyRAT
(that's [PyRAT](https://www.scionics.com/pyrat.html)] the animal facility software, not [Pyrat](http://www.pyratrum.com)] the rum).

## Installation for local use

First, prepare a virtual environment:

1. Create and activate a clean python 3 environment.
    ```
    virtualenv -p python3 config_venv --no-site-packages
    source config_venv/bin/activate
    ```
2. Install requirements
    ```
    pip3 install -r requirements.txt
    ```

## Preparation of AMS data

Next, export data from AMS. Export data from User, Stock, and Unit tables:

- User: export all columns into a new tab-delimited file named User.tsv
- Stock: export StockID, Name, State, and UserID into a new tab-delimited file named Stock.tsv
- Unit: export Name, State, SetupDate, SetupAmountMales, SetupAmountFemales, CurrentAmountMales, CurrentAmountFemales, FemaleStockID, MaleStockID, and UserID into a new tab-delimited file named Unit.tsv

These files should be in the same directory as the programs.

## Creation of PyRAT files

Run the programs in order:

1. Build the users.txt file:
   ```
   python3 export_ams_users.py
   ```
2. Build the strains.txt file:
   ```
   python3 export_ams_strains.py
   ```
3. Build the tanks.txt file:
   ```
   python3 export_ams_tanks.py
   ```
