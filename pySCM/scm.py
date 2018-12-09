import math

import matplotlib.pyplot as plt
import numpy as np

"""
Set the constants that are used for running the simple climate model at the beginning of the class.
(1) Carbon dioxide (CO2), methane (CH4), and nitrous oxide (N2O) concentrations at their pre-industrial level (e.g. 1750 values).
(2) CO2 emissions are reported in Peta grams of carbon (PgC) where 1 PgC = 10^15 g carbon and therefore we need the 
PgCperppm constant which is the conversion factor for PgC to ppm of CO2.
(3) We need estimates of direct (aerDirectFac) and indirect (aerIndirectFac) aerosol radiative forcing factors in units of (W/m^2)/TgS. 
"""
# -------------------------------------------------------------------------------
# These are our global variables
# -------------------------------------------------------------------------------
base_CO2 = 278.305  # [ppm]
base_CH4 = 700.0  # [ppb]
base_N20 = 270.0  # [ppb]

# PgC to ppm
PgCperppm = 2.123

# Direct and indirect RF factors 
aerDirectFac = -0.002265226
aerIndirectFac = -0.013558119


# -------------------------------------------------------------------------------
# Error handling.
# -------------------------------------------------------------------------------
class SCMError(Exception):
    """
    Error handling.
    """

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


# -------------------------------------------------------------------------------
# Emissions record
# -------------------------------------------------------------------------------
class EmissionRec:
    """
    We construct a class called EmissionRec which holds the atmospheric emissions of |CO2|, |CH4|, |N2O| and |SOx|.
    The emissions need to be provided as an input to the Simple Climate Model class, where the filename and path will be set in the
    *SimpleClimateModelParameterFile.txt*. The emissions will be read from file when the Simple Climate Model class is constructed by typing:

    >>> SCM = pySCM.SimpleClimateModel('PathAndFileNameOfParameterFile')
    """

    def __init__(self):
        self.CO2 = None
        self.CH4 = None
        self.SOx = None
        self.N2O = None


# -------------------------------------------------------------------------------
# Simple Climate Model Class
# -------------------------------------------------------------------------------

class SimpleClimateModel:
    """
    This is the Simple Climate Model class which can be created by typing:
    
    >>> SCM = pySCM.SimpleClimateModel('PathAndFileNameOfParameterFile')
    
    During the call of the constructor, all parameters detailed in the *SimpleClimateModelParameterFile.txt* will be read from file
    as well as the atmospheric emissions of GHGs (detailed above).
    
    .. note::
        The file containing the emissions should be in a certain format.
        Please refer to the example file (*EmissionsForSCM.dat*) for details.
    """

    def __init__(self, filename):
        """
        This is the constructor of the class. By calling the constructor, the emissions will be read from file 
        (filling the EmissionRec) and the parameters will be read from the parameter file.
        :param filename: path and filename of the parameter file.
        """
        self._read_parameters(filename)
        # get start and end year of simulation
        self.start_year = int(self._get_parameter('Start year'))
        self.end_year = int(self._get_parameter('End year'))
        self.emissions = self._read_emissions(self._get_parameter('File of emissions data'))

    def run_model(self, rf_flag=False):
        """ 
        This function runs the simple climate model. A number of private functions will be called but also a number of
        'independent' functions (detailed below). The model takes the atmosheric GHG emissions as input, converts them
        into concentrations and calculates the radiative forcing from the change in GHG concentrations over the years. Finally,
        the temperature change is derived from the change in radiative forcing which is required to calculate the change in sea
        level. For more information on the theory behind those calculations, please refer to 'Theory' page.
        
        To run the simple climate model, type:
        
        >>> SCM.run_model() 
        
        By default, the calculated temperature change and sea level change will be written to a textfile where the location and name
        of the textfile need to be specified in the parameter file. If the user wants to, a figure showing the temperature change and 
        sea level change, respectively, will be saved to file and again the path and filename have to be specified in the parameter file.   
        
        :param: rf_flag (bool) which is set to 'False' by default. If it is set to 'True' the function returns the calculated radiative forcing.
        :returns: This function returns the radiative forcing (numpy.array) if the flag was set to true. Otherwise, nothing will be returned.
        """
        sim_years = int(self._get_parameter('Years to evaluate response functions'))
        ocean_ml_depth = float(self._get_parameter('Ocean mixed layer depth [in meters]'))
        self.co2_concs = co2_emis_to_concs(self.emissions, sim_years, ocean_ml_depth)
        self.ch4_concs = ch4_emis_to_concs(self.emissions)
        self.n2o_concs = n2o_emis_to_concs(self.emissions)
        self.rf = calculate_rf(self.emissions, self.co2_concs, self.ch4_concs, self.n2o_concs)

        self.delta_temperature = calc_delta_surf_temp(sim_years, self.rf)
        self.slr = calculate_slr(sim_years, self.delta_temperature)

        self._save_temp_and_slr()

        if (rf_flag):
            return self.rf

    """
    Optional output can be produced, e.g. concentration output file & figure
    """

    def save_output(self):
        """
        This function is optional and allows the user to save the calculated GHG concentrations and also a figure showing the
        evolution of GHG concentrations. You can call this function by typing:
        
        >>> SCM.save_output()
         
        If this function gets called, the user has to make sure that the path and filenames are given in the parameter file.
        """
        # write to file if required
        filename = self._get_parameter('Write CH4 concentrations to file')
        if filename:
            self._write_concs_to_file('CH4', filename)

        # plot CH4 concentrations
        switch = self._get_parameter('Plot CH4 concentrations to file')
        if switch:
            self.plot('CH4', switch)

        # write to file if required
        filename = self._get_parameter('Write N20 concentrations to file')
        if filename:
            self._write_concs_to_file('N2O', filename)

        # plot N2O concentrations
        switch = self._get_parameter('Plot N2O concentrations to file')
        if switch:
            self.plot('N2O', switch)

        # write to file if required
        filename = self._get_parameter('Write CO2 concentrations to file')
        if filename:
            self._write_concs_to_file('CO2', filename)

        # plot CO2 concentrations
        switch = self._get_parameter('Plot CO2 concentrations to file')
        if switch:
            self.plot('CO2', switch)

    def _read_parameters(self, filename):
        """
        This private function will read all the parameters from the given parameter file. 
        The list of parameters will be stored in self._parameters which is a private dictionary. 
        """
        reader = open(filename, 'r')

        self._parameters = dict()
        for line in reader:
            pos = line.find('=')
            if pos > 1:
                tag = line[0:pos]
                value = line[pos + 1:].strip()
                self._parameters[tag] = value
        reader.close()

    def _get_parameter(self, key):
        """
        This private function will return the value (parameter) corresponding to the key provided.
        """
        try:
            result = self._parameters[key]
        except KeyError:
            result = None

        return result

    def _read_emissions(self, emis_fname):
        """
        |CO2|, |CH4|, |N2O| and |SOx| emissions will be read from file. The input file (Filename) has to be in a certain format.
        Please refer to the example file: EmissionsForSCM.dat. If there are missing values, this function will interpolate the
        values so that the emissions are available for the whole time period from startYr to endYr of the simulation.
        
        :param emis_fname: path and filename of the emissions file.
        :type: string
        :returns: nothing
        """

        # create empty list
        returnval = []
        # Set the length of the list. The length depends on the number of years.
        for i in range(self.end_year - self.start_year + 1):
            returnval.append(EmissionRec())

        # read data
        table = np.loadtxt(emis_fname, skiprows=3)

        for col in range(1, table.shape[1]):
            data = np.zeros((len(returnval)))
            data.fill(float('NaN'))
            for row in range(len(table)):
                index = int(table[row][0] - self.start_year)
                data[index] = table[row][col]

            # now you should have all data for one species
            # interpolate missing values
            x = np.arange(0, len(returnval))

            xp_hold = np.where(~np.isnan(data))[0]
            xp = np.zeros(len(xp_hold) + 1)
            xp[1:len(xp)] = xp_hold[0:len(xp_hold)]

            fp_hold = data[np.where(~np.isnan(data))[0]]
            fp = np.zeros(len(fp_hold) + 1)
            fp[1:len(fp)] = fp_hold[0:len(fp_hold)]

            interpolVal = np.interp(x, xp, fp)

            for index in range(len(interpolVal)):
                if col == 1:
                    returnval[index].CO2 = interpolVal[index]
                elif col == 2:
                    returnval[index].CH4 = interpolVal[index]
                elif col == 3:
                    returnval[index].N2O = interpolVal[index]
                elif col == 4:
                    returnval[index].SOx = interpolVal[index]

        return returnval

    # ---------------------------------------------------------
    # write and plot GHG concentrations to file (if required)
    # ---------------------------------------------------------

    def _write_concs_to_file(self, species, outputfilename):
        """
        This private function writes the calculated GHG concentrations for all years the simple climate model was running for to text 
        file. This function is called within the model and takes the calculated concentrations of the given species and the 
        output-filename as input. The user can set the output path and file name in the parameter file that gets given to the 
        model at initialisation. As this is a private function, this function should not be called by the user!   
        """
        if species == 'CO2':
            concs2write = self.co2_concs + base_CO2
            unit = "ppm"
        elif species == 'CH4':
            concs2write = self.ch4_concs + base_CH4
            unit = "ppb"
        elif species == 'N2O':
            concs2write = self.n2o_concs + base_N20
            unit = "ppb"

        writer = open(outputfilename, 'w')
        writer.write(
            "This files contains the CH4 concentrations [" + unit + "] for the years the model has been running for." + '\n')
        for i in range(len(concs2write)):
            writer.write(str(self.start_year + i) + "    " + str(concs2write[i]) + "\n")
        writer.close()

        # -----------------------------------------------

    # plot concentrations and save figures to file.
    # -----------------------------------------------

    def plot(self, species, output_filename):
        x = np.arange(self.start_year, self.end_year + 1)

        if species == 'CO2':
            concs2plot = self.co2_concs + base_CO2
            unit = "ppm"
        elif species == 'CH4':
            concs2plot = self.ch4_concs + base_CH4
            unit = "ppb"
        elif species == 'N2O':
            concs2plot = self.n2o_concs + base_N20
            unit = "ppb"
        else:
            raise SCMError('{} is not a valid species'.format(species))

        fig = plt.figure(1)
        plt.plot(x, concs2plot)
        # title and axes labels
        fig.suptitle(species + ' concentrations', fontsize=20)
        plt.xlabel('Year', fontsize=18)
        plt.ylabel(species + ' concentration [' + unit + ']', fontsize=18)
        # axes limits
        plt.xlim([self.start_year, self.end_year])
        plt.ylim([np.min(concs2plot), np.max(concs2plot)])
        # save figure to file
        plt.savefig(output_filename)
        plt.clf()

    def _save_temp_and_slr(self):
        """
        This private function saves the calculated temperature change and resulting sea level change to file. The path and filenames
        need to be provided in the parameter file. If the user also wants to save a figure showing the evolution of the temperature
        change and sea level change, the user also needs to provide the filename for the figure files in the parameter file.
        """
        try:
            filename = self._get_parameter('Filename for temperature change')
            if not filename:
                raise SCMError('You need to provide a filename in the Parameter set up file!')
                # write values to file
            writer = open(filename, 'w')
            writer.write(
                "This files contains change in temperature [degC] for the years the model has been run for." + '\n')
            for i in range(len(self.delta_temperature)):
                writer.write(str(self.start_year + i) + "    " + str(self.delta_temperature[i]) + "\n")
            writer.close()

            # Plot temperature change and save figure to file if required
            plot_file = self._get_parameter('Plot temperature change')
            if plot_file:
                x = np.arange(self.start_year, self.end_year + 1)
                fig = plt.figure(1)
                plt.plot(x, self.delta_temperature)
                # title and axes labels
                fig.suptitle(' Temperature change ', fontsize=20)
                plt.xlabel('Year', fontsize=18)
                plt.ylabel(' Temperature change [degC]', fontsize=18)
                # axes limits
                plt.xlim([self.start_year, self.end_year])
                plt.ylim([np.min(self.delta_temperature), np.max(self.delta_temperature)])
                # save figure to file
                plt.savefig(plot_file)
                plt.clf()

            sea_level_filename = self._get_parameter('Filename for sea level change')
            if not sea_level_filename:
                raise SCMError('You need to provide a filename in the Parameter set up file!')
                # write values to file
            writer = open(sea_level_filename, 'w')
            writer.write(
                "This files contains change in sea level [cm] for the years the model has been run for." + '\n')
            for i in range(len(self.slr)):
                writer.write(str(self.start_year + i) + "    " + str(self.slr[i]) + "\n")
            writer.close()

            # Plot temperature change and save figure to file if required
            plot_file = self._get_parameter('Plot sea level change')
            if plot_file:
                x = np.arange(self.start_year, self.end_year + 1)
                fig = plt.figure(1)
                plt.plot(x, self.slr)
                # title and axes labels
                fig.suptitle(' Sea level change ', fontsize=20)
                plt.xlabel('Year', fontsize=18)
                plt.ylabel(' Sea level change [m]', fontsize=18)
                # axes limits
                plt.xlim([self.start_year, self.end_year])
                plt.ylim([np.min(self.slr), np.max(self.slr)])
                # save figure to file
                plt.savefig(plot_file)
                plt.clf()
        except:
            raise


# -----------------------------------------------------------------------------
# Public functions which can be called outside the simple climate model class
# -----------------------------------------------------------------------------


def generate_biosphere_response(num_years):
    """
    This function calculates the decay response function for the biosphere.

    :param num_years: number of years to calculate the response function for.
    :returns: numpy.array -- contains the biosphere-atmospheric flux after initial carbon input per year
    """
    return_val = np.zeros(num_years)
    for yr in range(num_years):
        # Biosphere decay response function from Joos et al. 1996, pg. 416
        return_val[yr] = 0.7021 * np.exp(-0.35 * yr) + 0.01341 * np.exp(-yr / 20.0) - 0.7185 * np.exp(
            -0.4583 * yr) + 0.002932 * np.exp(-0.01 * yr)

    return return_val


def generate_ocean_response(num_years, OceanMLDepth):
    """
    This function calculates the ocean mixed layer response function (HILDA model) as described in Joos et al., 1996.
    This function returns the amount of carbon remaining in the surface layer of the ocean after an input (pulse) from the atmosphere
    scaled to units of micromol/kg.

    :param num_years: The number of years to calculate the response function for.
    :param OceanMLDepth: Ocean mixed layer depth in meters.
    :returns:  numpy.array -- contains the remaining carbon per year.
    """

    # ---------------------------------------------------------------------
    # The following constants were taken from Joos et al., 1996, pg 400.
    # ---------------------------------------------------------------------

    ocean_area = 3.62E14  # ocean area in square meters
    g_cper_mole = 12.0113  # molar mass of carbon.
    sea_water_dens = 1.0265E3  # sea water density in kg/m^3.

    return_val = np.zeros(num_years)

    for yr in range(num_years):
        if yr < 2.0:
            value = 0.12935 + 0.21898 * np.exp(-yr / 0.034569) + 0.17003 * np.exp(-yr / 0.26936) + 0.24071 * np.exp(
                -yr / 0.96083) + 0.24093 * np.exp(-yr / 4.9792)
        else:
            value = 0.022936 + 0.24278 * np.exp(-yr / 1.2679) + 0.13963 * np.exp(-yr / 5.2528) + 0.089318 * np.exp(
                -yr / 18.601) + 0.037820 * np.exp(-yr / 68.736) + 0.035549 * np.exp(-yr / 232.30)

        # scale values to micromole per kg
        return_val[yr] = value * (1E21 * PgCperppm / g_cper_mole) / (sea_water_dens * OceanMLDepth * ocean_area)

    return return_val


def delta_co2_from_ocean(ocean_surf_dic):
    """
    This function calculates the change in sea water |CO2| from equilibrium corresponding to change in ocean mixed layer carbon from
    equilibrium.

    :param ocean_surf_dic: Surface ocean dissolved inorganic carbon (DIC) [micromol/kg]
    :returns: the change in sea water |CO2| [ppm]
    """
    TC = 18.1716  # Effective Ocean temperature for carbonate chemistry in deg C.
    A1 = (1.5568 - 1.3993E-2 * TC)
    A2 = (7.4706 - 0.20207 * TC) * 1E-3
    A3 = -(1.2748 - 0.12015 * TC) * 1E-5
    A4 = (2.4491 - 0.12639 * TC) * 1E-7
    A5 = -(1.5468 - 0.15326 * TC) * 1E-10
    # from Joos et al. 1996, pg. 402
    return_val = ocean_surf_dic * (
            A1 + ocean_surf_dic * (A2 + ocean_surf_dic * (A3 + ocean_surf_dic * (A4 + ocean_surf_dic * A5))))

    return return_val


def co2_emis_to_concs(co2_emis, num_years, OceanMLDepth):
    """
    This function converts atmospheric |CO2| emissions to concentrations as described in Joos et al. 1996.
    
    :param co2_emis: atmospheric |CO2| emissions [PgC/year]
    :param num_years: number of years the response function is going to be calculated for
    :param OceanMLDepth: ocean mixed layer depth [m]
    :returns: numpy array -- containing the atmospheric |CO2| concentrations for each year [ppm]
    """
    # XAtmosBio is the amount of CO2 returned to the atmosphere as a result
    # of decay of the enhanced plant growth resulting from higher CO2.
    x_atmos_bio = 0.0
    air_sea_gas_exchange_coeff = 0.1042  # kg m^-2 year^-1
    biosphere_npp_0 = 60.0  # GtC/year.
    # 0.287 balances LUC emission of 1.1 PgC/yr in 1980s (Joos et al, 1996)
    # 0.380  balances LUC emission of 1.6 PgC/yr in 1980s (IPCC 1994)
    co2_fert_factor = 0.287
    co2ppm_0 = 278.305
    atmos_co2 = np.zeros(len(co2_emis))
    atmos_bio_flux = np.zeros(len(co2_emis))
    surface_ocean_dic = np.zeros(len(co2_emis))
    sea_water_pco2 = np.zeros(len(co2_emis))
    atmos_sea_flux = np.zeros(len(co2_emis))

    ocean_response = generate_ocean_response(num_years, OceanMLDepth)
    bio_response = generate_biosphere_response(num_years)

    for yr_ind in range(len(co2_emis) - 1):
        if yr_ind > 0:
            sea_water_pco2[yr_ind] = delta_co2_from_ocean(surface_ocean_dic[yr_ind])

        atmos_sea_flux[yr_ind] = air_sea_gas_exchange_coeff * (atmos_co2[yr_ind] - sea_water_pco2[yr_ind])
        # delta is the amount of CO2 taken out of the atmosphere due to stimulated plant growth minus the amount of CO2 returned
        # to the atmosphere due to the decay of organic material.
        delta = biosphere_npp_0 * co2_fert_factor * np.log(
            1.0 + (atmos_co2[yr_ind] / co2ppm_0)) / PgCperppm - x_atmos_bio
        x_atmos_bio += delta
        atmos_bio_flux[yr_ind] += x_atmos_bio
        # Accumulate committments of these fluxes to all future times for SurfaceOceanDIC and AtmosBioFlux.
        for j in range(yr_ind + 1, len(surface_ocean_dic)):
            surface_ocean_dic[j] = surface_ocean_dic[j] + atmos_sea_flux[yr_ind] * ocean_response[j - yr_ind]

        for j in range(yr_ind + 1, len(atmos_bio_flux)):
            atmos_bio_flux[j] = atmos_bio_flux[j] - x_atmos_bio * bio_response[j - yr_ind]

        atmos_co2[yr_ind + 1] = atmos_co2[yr_ind] + (co2_emis[yr_ind].CO2 / PgCperppm) - atmos_sea_flux[yr_ind] - \
                                atmos_bio_flux[yr_ind]

    return atmos_co2


def ch4_emis_to_concs(emissions):
    """
    This function converts methane (|CH4|) emissions into concentrations.
    
    :param emissions: |CH4| emissions [TgCH4/year]
    :returns: numpy.array -- containing the |CH4| concentrations for each year [ppb]
    """
    tau_ch4 = 10.0  # Lifetime of CH4
    lam_ch4 = 1.0 / tau_ch4  # inverse lifetime in years-1
    scale_ch4 = 2.78  # TgCH4 per ppb (IPCC TAR report value, chapter 4)

    result = np.zeros(len(emissions))
    decay = np.exp(-lam_ch4)
    accum = (1.0 - decay) / (lam_ch4 * scale_ch4)
    for i in range(1, len(emissions)):
        result[i] = result[i - 1] * decay + emissions[i - 1].CH4 * accum

    return result


def n2o_emis_to_concs(emissions):
    """
    This function converts nitrous oxide (|N2O|) emissions into concentrations.
    
    :param emissions: |N2O| emissions [TgN2O/year]
    :returns: numpy.array -- containing the |N2O| concentrations for each year [ppb]
    """
    tau_n2o = 114.0  # Lifetime of N2O
    lam_n2o = 1.0 / tau_n2o  # inverse lifetime in years-1
    scale_n2o = 4.8  # TgN2O per ppb (IPCC TAR report value, chapter 4)

    result = np.zeros(len(emissions))
    decay = np.exp(-lam_n2o)
    accum = (1.0 - decay) / (lam_n2o * scale_n2o)
    for i in range(1, len(emissions)):
        result[i] = result[i - 1] * decay + emissions[i - 1].N2O * accum

    return result


def calculate_rf(emissions, co2_concs, ch4_concs, n2o_concs):
    """
    This function calculates the total radiative forcing (formula given in IPCC TAR Chapter 6). The total change in radiative forcing 
    is the sum of the changes in radiative forcing resulting from changes in |CO2|, |CH4|, and |N2O| concentrations and sulfate 
    emissions.
    
    :param emissions: |SOx| emissions [TgS/year]
    :param co2_concs: |CO2| concentrations [ppm]
    :param ch4_concs: |CH4| concentrations [ppb]
    :param n2o_concs: |N2O| concentrations [ppb]
    :returns: numpy.array -- containing the change in radiative forcing per year.
    """
    rad_forcing_ch4 = np.zeros(len(emissions))
    rad_forcing_n2o = np.zeros(len(emissions))

    # changes in radiative forcing due to changes in CO2 concentrations
    rad_forcing_co2 = 5.35 * np.log(1 + (co2_concs / base_CO2))

    # changes in radiative forcing due to changes in CH4 concentrations
    for i in range(len(emissions)):
        # the two functions below (fnow/fthen) account for the fact that methane and nitrous oxide have overlapping absoption bands so that higher concentrations of one gas will reduce the
        # effective absoption by the other and vice versa.
        fnow = 0.47 * np.log(
            1 + 2.01e-5 * (((base_CH4 + ch4_concs[i]) * base_N20) ** 0.75) + 5.31e-15 * (base_CH4 + ch4_concs[i]) * (
                    ((base_CH4 + ch4_concs[i]) * base_N20) ** 1.52))
        fthen = 0.47 * np.log(
            1 + 2.01e-5 * ((base_CH4 * base_N20) ** 0.75) + 5.31e-15 * base_CH4 * ((base_CH4 * base_N20) ** 1.52))
        rad_forcing_ch4[i] = 0.036 * (math.sqrt(base_CH4 + ch4_concs[i]) - math.sqrt(base_CH4)) - (fnow - fthen)

    # changes in radiative forcing due to changes in N2O concentrations
    for i in range(len(emissions)):
        fnow = 0.47 * np.log(1 + 2.01e-5 * ((base_CH4 * (base_N20 + n2o_concs[i])) ** 0.75) + 5.31e-15 * base_CH4 * (
                (base_CH4 * (base_N20 + n2o_concs[i])) ** 1.52))
        fthen = 0.47 * np.log(
            1 + 2.01e-5 * ((base_CH4 * base_N20) ** 0.75) + 5.31e-15 * base_CH4 * ((base_CH4 * base_N20) ** 1.52))
        rad_forcing_n2o[i] = 0.12 * (math.sqrt(base_N20 + n2o_concs[i]) - math.sqrt(base_N20)) - (fnow - fthen)

    # changes in radiative forcing due to changes in SOx emissions
    rad_forcing_sox = np.array([(aerDirectFac + aerIndirectFac) * emissions[i].SOx for i in range(len(emissions))])

    # sum 
    totalRadForcing = rad_forcing_co2 + rad_forcing_ch4 + rad_forcing_n2o + rad_forcing_sox

    return totalRadForcing


def calc_delta_surf_temp(num_years, radForcing):
    """
    This function calculates the temperature change due to changes in radiative forcing.
    
    :param num_years: number of years the temperature response function will be evaluated for.
    :param radForcing: changes in radiative forcing due to changes in |CO2|, |CH4|, |N2O| concentrations and |SOx| emissions.
    :return: numpy.array --containing the temperature change for every year.
    """

    # climate sensitivity := the equilibrium change in global mean surface temperature following a doubling of the atmospheric equivalent CO2 concentration
    climate_sensitivity = 1.1  # (4.114/3.74)
    result = np.zeros(len(radForcing))

    def generate_temp_response_function(numYrs):
        """
        This function calculates the temperature response function that is used to calculate the change in global mean surface
        temperature as a result of changes in radiative forcing.

        :param numYrs: number of years the response function will be evaluates for.
        :returns: numpy.array -- containing climate response function
        """
        # The values below were determined by fitting a double exponentional impulse response function model (see documentation) to values from a HadCM3 4xCO2 simulation.
        result = np.array(
            [(0.59557 / 8.4007) * np.exp(-i / 8.4007) + (0.40443 / 409.54) * np.exp(-i / 409.54) for i in
             range(numYrs)])

        return result

    tempResFunc = generate_temp_response_function(num_years)

    for i in range(len(radForcing)):
        for j in range(i, len(radForcing)):
            result[j] = result[j] + radForcing[i] * tempResFunc[j - i]

    result = result * climate_sensitivity

    return result


def calculate_slr(num_years, tempChange):
    """
    This function calculated the changes in sea level due to changes in global mean surface temperatures.
    
    :param num_years: number of years the sea level response function will be evaluated for.
    :param tempChange: changes in global mean surface temperature due to changes in |CO2|, |CH4|, |N2O| concentrations and |SOx| emissions.
    :return: numpy.array -- containing the sea level change for every year.
    """
    result = np.zeros(len(tempChange))

    def generate_slr_response(numYrs):
        """
        This function calculates the sea level response function that is used to calculate the change in sea level as a result of changes in in global mean surface temperature.
        This equation only accounts for changes in sea level resulting from thermal expansion of the ocean, it does not include the effects of melting glaciers and melting grounded
        ice sheets.

        :param numYrs: number of years the response function will be evaluates for.
        :returns: numpy.array -- containing climate response function
        """
        # The values below were determined by fitting a double exponentional impulse response function model (see documentation) to values from a HadCM3 4xCO2 simulation.
        result = (
            [(0.96677 / 1700.2) * np.exp(-i / 1700.2) + (0.03323 / 33.788) * np.exp(-i / 33.788) for i in
             range(numYrs)])

        return np.array(result)

    seaLevelResFunc = generate_slr_response(num_years)

    for i in range(len(tempChange)):
        for j in range(i, len(tempChange)):
            result[j] = result[j] + tempChange[i] * seaLevelResFunc[j - i]

    return result
