.. |CO2| replace:: CO\ :sub:`2`
.. |CH4| replace:: CH\ :sub:`4`
.. |N2O| replace:: N\ :sub:`2`\ O
.. |SOx| replace:: SO\ :sub:`x`

Documentation of the pySCM package
***********************************

In the following we will descibe the Simple Climate Model class and its public functions and methods. To run the simple climate model
two input files are required:

(1) Parameter file (*SimpleClimateModelParameterFile.txt*) that sets parameters for the Simple Climate model run such as the start and end year of the simulation
as well as the path and file names for the input and output files.

(2) The emission file (*EmissionsForSCM.dat*) containing the atmospheric emissions of carbon dioxid (|CO2|), methane (|CH4|),
nitrous oxide (|N2O|) and sulfate (|SOx|).

-----------------
Global constants
-----------------

At the beginning of the Simple Climate Model class we define a set the global variables as constants.
These variables will be used throughout the simple climate model run and therefore need to be global:

+ Carbon dioxide (|CO2|), methane (|CH4|), and nitrous oxide (|N2O|) concentrations at their pre-industrial level (e.g. 1750 values).

	baseCO2 = 278.305

	baseCH4 = 700.0

	baseN2O = 270.0

+ CO2 emissions are reported in Peta grams of carbon (PgC) where 1 PgC = 10^15 g carbon and therefore we need the PgCperppm constant which is the conversion factor for PgC to ppm of CO2.

	PgCperppm = 2.123

+ Estimates of direct (aerDirectFac) and indirect (aerIndirectFac) aerosol radiative forcing factors in units of (W/m^2)/TgS are:

	aerDirectFac = -0.002265226

	aerIndirectFac = -0.013558119

--------------------------------
Description of the pySCM module
--------------------------------

""""""""""""""""""""""""""""""""
Emission record Class
""""""""""""""""""""""""""""""""

.. autoclass:: pySCM.scm.EmissionRec
   :members:


""""""""""""""""""""""""""""""""
Simple Climate Model Class
""""""""""""""""""""""""""""""""

The Simple Climate Model class comprises only two public functions, i.e. runModel and saveOutput. The class uses the EmissionRec to store all GHG emissions that are going to be used during the model run.

.. autoclass:: pySCM.SimpleClimateModel
   :members:

"""""""""""""""""""""""""""""""""""""""""
Independent public functions and methods
"""""""""""""""""""""""""""""""""""""""""

These are public functions that will be called within the Simple Climate Model but can also be called outside the class. By providing the
right input, these functions can be used independently of the Simple Climate Model class, e.g.

>>> pySCM.CO2EmissionsToConcs(Emissions, numYr, OceanMLDepth)

where emissions are the |CO2| emissions, numYr are the number of years the response function will be calculated for and OceanMLDepth is the ocean layer depth. More information are given in the code or
in the 'Theory' part of this documentation.

.. automodule:: pySCM.scm.SimpleClimateModel
   :members: CO2EmissionsToConcs, CH4EmssionstoConcs, N2OEmssionstoConcs, CalcRadForcing, GenerateTempResponseFunction, GenerateSeaLevelResponseFunction, GenerateOceanResponseFunction, GenerateBiosphereResponseFunction, DeltaSeaWaterCO2FromOceanDIC, CalculateTemperatureChange, CalculateSeaLevelChange





