# BioSNICAR Functions

Here you will find reference documentation for all the BioSNICAR model functions, organized by module.

## classes module

This module contains class definitions for all the classes used in BioSNICAR. This includes the following classes:

- `Impurity`
- `Ice`
- `Illumination`
- `RTConfig`
- `ModelConfig`
- `PlotConfig`
- `Outputs`
- `BioOpticalConfig`

These classes are used as convenient, mutable containers for the necessary data required to run BioSNICAR. They are automatically instantiated by calling `setup_snicar()` using values provided in `inputs.yaml`. Class functions are available for recalculating derived attributes when the
user changes attributes of `Ice` or `Illumination` classes.

### Impurity (class)

Light absorbing impurity.

Instances of Impurity are one discrete type of light absorbing impurity with a distinct set of optical properties.

#### Attributes:
    name: name of impurity
    cfactor: concentration factor used to convert field measurements to model config (default=1)
    unit: the unit the concentration should be represented in (0 = ppb, 1 = cells/mL)
    conc: concentration of the impurity in each layer (in units of self.unit)
    file: name of netCDF file containing optical properties and size distribution
    impurity_properties: instance of opened file self.file
    mac: mass absorption coefficient (m2/kg or m2/cell)
    ssa: single scattering albedo
    g: asymmetry parameter


### Ice (class)
Snow or ice column physical properties.

Instances of Ice contain all the physical properties of each vertical layer of the
snow or ice column and the underlying surface.

#### Attributes:
    dz: array containing thickness of each layer in m
    layer_type: array containing type (0 = grains, 1 = solid ice) in each layer
    cdom: array containing Boolean (1/0) toggling presence of cdom in each layer
    rho: array containing density of each layer in kg/m3
    sfc: array with reflectance of underlying surface per wavelength
    rf: refractive index to use, 0,1,2 or 3 (see docs for definition)
    shp: grain shape per layer where layer_type==1
    rds: grain radius (layer_type==0) or bubble radius (layer_type==0) in each layer
    water: radius of grain+water coating in each layer where layer_type==0
    hex_side: length of each side of hexagonal face for grain_shp==4
    hex_length: column length for hexagonal face for grain_shp==4
    shp_fctr: ratio of nonspherical eff radii to equal vol sphere, in each layer
    ar: aspect ratio of grains in each layer where layer_type==0
    nbr_lyr: number of vertical layers

#### functions
##### calculate_refractive_index

Calculates ice refractive index from initialized class attributes.

Takes self.rf and config from inpouts.yaml and uses them to calculate
new attributes related to the ice refractive index.

###### Args
    self

###### Returns
    ref_idx_im: imaginary part of refractive index
    ref_idx_re: real part of refractive index
    fl_r_dif_a: precomputed diffuse reflectance "perpendicular polarized)
    fl_r_dif_b: precomputed diffuse reflectance "parallel polarized)
    op_dir: directory containing optical properties

###### Raises
    ValueError if rf out of range

### Illumination (class)

Properties of incoming irradiance.
Instances of Illumination contain all data relating to the incoming irradiance.

#### Attributes:
    direct: Boolean toggling between direct and diffuse irradiance
    solzen: solar zenith angle in degrees from the vertical
    incoming: choice of spectral distribution from file 0-6
    flx_dir: directory containing irradiance files
    stubs: array of stub strings for selecting irradiance files
    nbr_wvl: number fo wavelengths (default 480)

#### Functions
##### calculate_irradiance

Calculates irradiance from initialized attributes.

Takes mu_not, incoming and file stubs from self and calculates irradiance.

###### Args
    self

###### Returns:
    flx_slr: incoming flux from file
    Fd: diffuse irradiance
    Fs: direct irradiance


###### Raises
    ValueError is incoming is out of range

### RTConfig

Radiative transfer configuration.

#### Attributes:
    aprx_type: choice of two-stream approximation (0-2)
    delta: Boolean to toggle delta transformation (0/1)


### ModelConfig (class)


## adding_doubling_solver module

Here the ice/impurity optical properties and illumination conditions are used to calculate energy fluxes between the ice, atmosphere and
underlying substrate.

Typically this function would be called from snicar_driver() because it takes as inputs intermediates that are calculated elsewhere.
Specifically, the functions setup_snicar(), get_layer_OPs() and mix_in_impurities() are called to generate tau, ssa, g and L_snw,
which are then passed as inputs to adding_doubling_solver().

The adding-doubling routine implemented here originates in Brieglib and Light (2007) and was coded up in Matlab by Chloe Whicker and Mark
Flanner to be published in Whicker (2022: The Cryosphere). Their scripts were the jumping off point for this script and their code is still
used to benchmark this script against.

The adding-doubling solver implemented here has been shown to do an excellent job at simulating solid glacier ice. This solver can either treat ice as a "granular" material with a bulk medium of air with discrete ice grains, or as a bulk medium of ice with air inclusions. In the latter case, the upper
boundary is a Fresnel reflecting surface. Total internal reflection is accounted for if the irradiance angles exceed the critical angle.

This is always the appropriate solver to use in any  model configuration where solid ice layers and fresnel reflection are included.


### adding_doubling_solver:

Control function for the adding-doubling solver.
Makes function calls in sequence to generate, then return, an instance of `Outputs`.

#### Args:
    
    tau: optical thickness of ice column in m/m
    ssa: single scattering albedo of ice column (dimensionless)
    g: asymmetry parameter for ice column
    L_snw: mass of ice in lg
    ice: instance of Ice class
    illumination: instance of Illumination class
    model_config: instance of ModelConfig class

#### Returns:
    
    outputs: Instance of Outputs class

#### Raises:
    
    ValueError if violation of conservation of energy detected


### calc_reflectivity_transmittivity
Calculates reflectivity and transmissivity.
Sets up new variables, applies delta transformation and makes initial calculations of reflectivity and transmissivity in each layer.

#### Args:
    tau0: initial optical thickness
    ssa0: initial single scattering albedo
    g0: initial asymmetry parameter
    lyr: index of current layer
    model_config: instance of ModelConfig class
    exp_min: small number to avoid /zero error
    rdif_a: reflectivity to diffuse irradiance at polarization angle == perpendicular
    tdif_a: transmissivity to diffuse irradiance at polarization angle == perpendicular
    trnlay: transmission through layer
    mu0n: incident beam angle adjusted for refraction
    epsilon: small number to avoid singularity
    rdir: reflectivity to direct beam
    tdir: transmissivity to direct beam

#### Returns:
    rdir:
    tdir:
    ts:
    ws:
    gs:
    lm:

### define_constants_arrays
    Defines and instantiates constants required for adding-doubling calculations.
    Defines and instantiates all variables required for calculating energy fluxes using the adding-doubling method.

#### Args:
    tau: optical thickness of ice column in m/m
    g: asymmetry parameter for ice column
    ssa: single scattering albedo of ice column (dimensionless)
    ice: instance of Ice class
    illumination: instance of Illumination class
    model_config: instance of ModelConfig class

#### Returns:
    tau0: initial optical thickness (m/m)
    g0: initial asymmetry parameter (dimensionless)
    ssa0: initial single scatterign albedo (dimensionless)
    epsilon: small number to avoid singularity
    exp_min: small number to avoid zero calcs
    nr: real part of refractive index
    mu0: cosine of direct beam zenith angle
    mu0n: adjusted cosine of direct beam zenith angle after refraction
    trnlay: transmission through layer
    rdif_a: reflectivity to diffuse irradiance at polarization angle == perpendicular
    rdif_b: reflectivity to diffuse irradiance at polarization angle == parallel
    tdif_a: transmissivity to diffuse irradiance at polarization angle == perpendicular
    tdif_b: transmissivity to diffuse irradiance at polarization angle == parallel
    rdir: reflectivity to direct beam
    tdir: transmissivity to direct beam
    lyrfrsnl: index of uppermost fresnel reflecting layer in ice column
    trnlay:
    rdif_a:
    rdif_b:
    tdif_a:
    tdif_b:
    rdir:
    tdir:
    rdndif:
    trntdr:
    trndir:
    trndif:
    fdirup:
    fdifup:
    fdirdn:
    fdifdn:
    dfdir:
    dfdif:
    F_up:
    F_dwn:
    F_abs:
    F_abs_vis:
    F_abs_nir:
    rupdif:
    rupdir:


### calc_reflection_transmission_from_top

alculates the reflection and transmission of energy at top surfaces.

Calculate the solar beam transmission, total transmission, and reflectivity for diffuse radiation from below at interface lyr, the top of the current layer lyr.

#### Args:
    lyr: integer representing the index of the current layer (0 at top)
    trnlay: transmissivity of current layer
    rdif_a: reflectivity to diffuse irradiance at polarization state == perpendicular
    rdir: reflectivity to direct beam
    tdif_a: transmissivity to diffuse irradiance at polarization state == perpendicular
    rdif_b: reflectivity to diffuse irradiance at polarization state == parallel
    tdir: transmissivity to direct beam
    tdif_b: transmissivity to diffuse irradiance at polarization state == parallel
    model_config: instance of ModelConfig class
    ice: instance of Ice class
    trndir:
    rdndif:
    trntdr:
    trndif:

#### Returns:
    trndir: transmission of direct beam
    trntdr: total transmission of direct beam for all layers above current layer
    rdndif: downwards diffuse reflectance
    trndif: diffuse transmission

### apply_gaussian_integral

Applies gaussian integral to integrate over angles. Uses Gaussian integration to integrate fluxes hemispherically from N reference angles where N = len(gauspt) (default is 8).

#### Args:
    model_config: instance of ModelConfig class
    exp_min: small number for avoiding div/0 error
    ts: delta-scaled extinction optical depth for lyr
    ws: delta-scaled single scattering albedo for lyr
    gs: delta-scaled asymmetry parameter for lyr
    epsilon: small number to avoid singularity
    lm: lamda for use in delta scaling
    lyr: integer representing index of current layer (0==top)
    rdif_a: rdif_a: reflectance to diffuse energy w polarization state == perpendicular
    tdif_a: rdif_a: transmittance to diffuse energy w polarization state == perpendicular

#### Returns:
    smt: accumulator for tdif gaussian integration
    smr: accumulator for rdif gaussian integration
    swt: sum of gaussian weights

### update_transmittivity_reflectivity

Updates transmissivity and reflectivity values after iterations.

#### Args:
    swt: sum of gaussian weights (for integrating over angle)
    smr: accumulator for rdif gaussian integration
    smt: accumulator for tdif gaussian integration
    lyr: integer representign index of current layer (0 == top)
    rdif_a: reflectance to diffuse energy w polarization state == perpendicular
    rdif_b: reflectance to diffuse energy w polarization state == parallel
    tdif_a: transmittance to diffuse energy w polarization state == perpendicular
    tdif_b: transmittance to diffuse energy w polarization state == parallel

#### Returns:
    rdif_a: updated reflectance to diffuse energy w polarization state == perpendicular
    rdif_b: updated reflectance to diffuse energy w polarization state == parallel
    tdif_a: updated transmittance to diffuse energy w polarization state == perpendicular
    tdif_b: updated transmittance to diffuse energy w polarization state == parallel


### calc_correction_fresnel_layer

Calculates correction for Fresnel reflection and total internal reflection.
Corrects fluxes for Fresnel reflection in cases where total internal reflection does and does not occur (angle > critical_angle).
In TIR case fluxes are precalculated because ~256 gaussian points required for convergence.

#### Args:
    model_config: instance of ModelConfig class
    ice: instance of Ice class
    illumination: instance of Illumination class
    mu0n: incidence angle for direct beam adjusted for refraction
    mu0: incidence angle of direct beam at upper surface
    nr: real part of refractive index
    rdif_a: reflectance to diffuse energy w polarization state == perpendicular
    rdif_b: reflectance to diffuse energy w polarization state == parallel
    tdif_a: transmittance to diffuse energy w polarization state == perpendicular
    tdif_b: transmittance to diffuse energy w polarization state == parallel
    trnlay: transmission of layer == lyr
    lyr: current layer (0 ==top)
    rdir: reflectance to direct beam
    tdir: transmission of direct beam


#### Returns:
    rdif_a: updated reflectance to diffuse energy w polarization state == perpendicular
    rdif_b: updated reflectance to diffuse energy w polarization state == parallel
    tdif_a: updated transmittance to diffuse energy w polarization state == perpendicular
    tdif_b: updated transmittance to diffuse energy w polarization state == parallel
    trnlay: updated transmission of layer == lyr
    rdir: updated reflectance to direct beam
    tdir: updated transmission of direct beam

### calc_reflection_below

Calculates dir/diff reflectyivity for layers below surface.
Computes reflectivity to direct (rupdir) and diffuse (rupdif) radiation for layers below by adding succesive layers starting from the underlying ice and working upwards.

#### Args:
    model_config: instance of ModelConfig class
    ice: instance of Ice class
    rdif_a: reflectance to diffuse energy w polarization state == perpendicular
    rdif_b: reflectance to diffuse energy w polarization state == parallel
    tdif_a: transmittance to diffuse energy w polarization state == perpendicular
    tdif_b: transmittance to diffuse energy w polarization state == parallel
    trnlay: transmission of layer == lyr
    rdir: reflectance to direct beam
    tdir: transmission of direct beam
    rupdif: upwards flux direct
    rupdir: upwards flux diffuse

#### Returns:
    rupdir: upwards flux direct
    rupdif: upwards flux diffuse


### trans_refl_at_interfaces
    """Calculates transmission and reflection at layer interfaces.

#### Args:
    model_config: instance of ModelConfig class
    ice: instance of Ice class
    rupdif: total diffuse radiation reflected upwards
    rupdir: total direct radiation reflected upwards
    rdndif: downwards reflection of diffuse radiation
    trndir: transmission of direct radiation
    trndif: transmission of diffuse radiation
    trntdr: total transmission
    fdirup:
    fdirdn:
    fdifup:
    fdifdn:
    dfdir:
    dfdif:

#### Returns:
    fdirup: upwards flux of direct radiation
    fdifup: upwards flux of diffuse radiation
    fdirdn: downwards flux of direct radiation
    fdifdn: downwards flux of diffuse radiation


### calculate_fluxes

Calculates total fluxes in each layer and for entire column.

#### Args:
    model_config: instance of ModelConfig class
    ice: instance of Ice class
    illumination: instance of Illumination class
    fdirup: upwards flux of direct radiation
    fdifup: upwards flux od diffuse radiation
    fdirdn: downwards flux of direct radiation
    fdifdn: downwards flux of diffuse radiation
    F_up:
    F_dwn:
    F_abs:
    F_abs_vis:
    F_abs_nir:

#### Returns:
    albedo: ratio of upwards fluxes to incoming irradiance
    F_abs: absorbed flux in each layer
    F_btm_net: net fluxes at bottom surface
    F_top_pls: upwards flux from upper surface


### conservation_of_energy_check

hecks there is no conservation of energy violation.

#### Args:
    illumination: instance of Illumination class
    F_abs: absorbed flux in each layer
    F_btm_net: net flux at bottom surface
    F_top_pls: upwards flux from upper boundary

#### Returns:
    None

#### Raises:
    ValueError is conservation of energy error is detected


### get_outputs

Assimilates useful data into instance of Outputs class.

#### Args:
    illumination: instance of Illumination class
    albedo: ratio of upwwards fluxes and irradiance
    model_config: instance of ModelConfig class
    L_snw: mass of ice in each layer
    F_abs: absorbed flux in each layer
    F_btm_net: net flux at bottom surface

#### Returns:
    outputs: instance of Outputs class


## biosnicar.bubble_reff_calculator module
Calculates effective radius of air bubbles.

This script is for taking specific surface area for bubbly ice an calculating the effective radius of the bubbles assuming a lognormal bubble size distribution.

The reason this is required is that the well-known conversion between SSA and r_eff:

r_eff = 3/(P_i * SSA) where P_i is density of ice (917 kg m-3)

gives the effective radius of a discrete grain of given SSA, for a collection of bubbles in a bulk medium of ice a more nuanced calculation is required.

The derivation of the calculations are explained in the pdf ./assets/SSA_derivation.pdf from Chloe Whicker (UMich).

biosnicar.classes module
Classes used in BioSNICAR.

This module contains class definitions for all the classes used in BioSNICAR. This includes:

Impurity Ice Illumination RTConfig ModelConfig PlotConfig Outputs BioOpticalConfig

These classes are used as convenient, mutable containers for the necessary data required to run BioSNICAR. They are automatically instantiated by calling setup_snicar() using values provided in inputs.yaml. Class functions are available for recalculating derived attributes when the user changes attributes of Ice or Illumination classes.

classclasses.BioOpticalConfig(input_file)[source]
Bases: object

Configuration class for bio-optical model.

wvl
(numpy array, default: np.arange(0.200, 4.999, 0.001)) wavelengths in spectral range of interest (in µm, 1nm step)

wet_density
(int - used if biomass: True) density of wet biomass

(kg/m3 - 1060 and 1160 for snow and glacier algae,Chevrollier et al. 2022)
dry_density
(int - used if biomass: True) density of dry biomass (kg/m3 - 625 and 684 for snow and glacier algae, Chevrollier et al. 2022)

ABS_CFF_CALC
toggles calculating abs_cff from pigments or loading from file.

abs_cff_loaded_reconstructed
(boolean) True if the abs_cff is loaded as a reconstructed spectrum from pigment absorbance (see methods in Chevrollier et al. 2022)

abs_cff_loaded_invivo
(boolean) True if the abs_cff is loaded as in vivo spectra of whole cells

abs_cff_file
(string) directory to the abs_cff file if loaded

pigment_data
dictionary with pigment file names and associated intracellular concentrations (ng/cell, ng/µm3 or ng/ng)

pigment_dir
(string) used if abs_cff_calculated is True, directory to folder containing pigment mass absorption coefficients that must be csv file with size and resolution of wvl, and units in m2/mg

packaging_correction_SA
(boolean - applied ONLY if abs_cff_loaded_reconstructed is True) if True, reconstructed SA abs_cff is corrected for pigment packaging following Chevrollier et al. 2022

packaging_correction_GA
(boolean - applied ONLY if abs_cff_loaded_reconstructed is True) if True, reconstructed GA abs_cff is corrected for pigment packaging following Chevrollier et al. 2022

dir_pckg
(string) directory to pigment packaging correction files

k_water_dir
(string) path to file with imaginary part of the refractive index of water

unit
unit for absorption cross section: 0 = m2/cell, 1 = m2/um3, 3 = m2/mg and/or pigment data: 0 = ng/cell, 1 = ng/um3, 3 = ng/mg

cell_vol
(int - used if cellular: True) volume of the algae cell (um3)

n_algae
(int) real part of cellular refractive index in the spectral range of wvl (constant 1.38 by default, Chevrollier et al. 2022)

GO
(boolean) if True, uses geometric optics equations (Cook et al. 2020 adapted from Diedenhoven et al (2014)) to calculate single scattering OPs assuming cell shape: cylinder

Mie
(boolean) if True, uses Mie theory to calculate single scattering OPs assuming cell shape: sphere

radius
(int) radius of sphere (Mie)/cynlinder (GO) representing cell (µm)

length
(int) depth of the cylinder representing the cell (GO option, µm)

report_dims
(boolean) if True, cell dimensions printed to console

plot_ssps
(boolean) if True, print plots with ssps

savefig_ssps
if True, ssps plots saved in the directory savepath

plot_n_k_abs_cff
(boolean) if True, plot with n,k and abs_cff printed

saveplots_n_k_abs_cff
(boolean) if True, plots saved in the directory savepath

savefiles_n_k_abs_cff
(boolean) if True, files with k,n and abs_cff saved in the directory savepath

savepath
(boolean) directory for saving data if savefiles or saveplots toggled on

smooth
(boolean) if True, apply optional smoothing filter

window_size
(int) size of window of smoothing filter (dflt value: 25)

poly_order
(int) polynomial order of smoothing filter (dflt value: 3)

save_netcdf =
Type
boolean

savepath_netcdf =
Type
string

filename_netcdf =
optical properties

Type
string

information =
metadata in netcdf (e.g. ‘Glacier algae OPs derived from GO calculations with empirical abs_cff’)

Type
string

validate_biooptical_inputs()[source]
classclasses.Ice(input_file)[source]
Bases: object

Snow or ice column physical properties.

Instances of Ice contain all the physical properties of each vertical layer of the snow or ice column and the underlying surface.

dz
array containing thickness of each layer in m

layer_type
array containing type (0 = grains, 1 = solid ice) in each layer

cdom
array containing Boolean (1/0) toggling presence of cdom in each layer

rho
array containing density of each layer in kg/m3

sfc
array with reflectance of underlying surface per wavelength

rf
refractive index to use, 0,1,2 or 3 (see docs for definition)

shp
grain shape per layer where layer_type==1

rds
grain radius (layer_type==0) or bubble radius (layer_type==0) in each layer

water
radius of grain+water coating in each layer where layer_type==0

hex_side
length of each side of hexagonal face for grain_shp==4

hex_length
column length for hexagonal face for grain_shp==4

shp_fctr
ratio of nonspherical eff radii to equal vol sphere, in each layer

ar
aspect ratio of grains in each layer where layer_type==0

nbr_lyr
number of vertical layers

calculate_refractive_index(input_file)[source]
Calculates ice refractive index from initialized class attributes.

Takes self.rf and config from inpouts.yaml and uses them to calculate new attributes related to the ice refractive index.

Parameters
self –

Returns
ref_idx_im – imaginary part of refractive index

ref_idx_re – real part of refractive index

fl_r_dif_a – precomputed diffuse reflectance “perpendicular polarized)

fl_r_dif_b – precomputed diffuse reflectance “parallel polarized)

op_dir – directory containing optical properties

Raises
ValueError if rf out of range –

classclasses.Illumination(input_file)[source]
Bases: object

Properties of incoming irradiance.

Instances of Illumination contain all data relating to the incoming irradiance.

direct
Boolean toggling between direct and diffuse irradiance

solzen
solar zenith angle in degrees from the vertical

incoming
choice of spectral distribution from file 0-6

flx_dir
directory containing irradiance files

stubs
array of stub strings for selecting irradiance files

nbr_wvl
number fo wavelengths (default 480)

calculate_irradiance()[source]
Calculates irradiance from initialized attributes.

Takes mu_not, incoming and file stubs from self and calculates irradiance.

Parameters
self –

Returns
flx_slr – incoming flux from file

Fd – diffuse irradiance

Fs – direct irradiance

Raises
ValueError is incoming is out of range –

classclasses.Impurity(file, coated, cfactor, unit, name, conc)[source]
Bases: object

Light absorbing impurity.

Instances of Impurity are one discrete type of light absorbing impurity with a distinct set of optical properties.

name
name of impurity

cfactor
concentration factor used to convert field measurements to model config (default=1)

unit
the unit the concentration should be represented in (0 = ppb, 1 = cells/mL)

conc
concentration of the impurity in each layer (in units of self.unit)

file
name of netCDF file containing optical properties and size distribution

impurity_properties
instance of opened file self.file

mac
mass absorption coefficient (m2/kg or m2/cell)

ssa
single scattering albedo

g
asymmetry parameter

classclasses.ModelConfig(input_file)[source]
Bases: object

Model configuration.

smooth
Boolean to toggle savitsky-golay filter to smooth albedo

window_size
window size to use for smoothing func

poly_order
order of polynomial used to smooth albedo

dir_base
base directory

dir_wvl
path to wavelengths in csv file

sphere_ice_path
directory containing OPs for spherical ice grains

hex_ice_path
directory containing OPs for hexagonal ice grains

bubbly_ice_path
directory containing OPs for bubbly ice

ri_ice_path
path to file containing pure ice refractive index

op_dir_stubs
sstring stubs for ice optical property files

wavelengths
array of wavelengths in nm (default 0.205 - 4.995 um)

nbr_wvl
number of wavelengths (default 480)

vis_max_idx
index for upper visible wavelength (default 0.75 um)

nir_max_idx
index for upper NIR wavelength (default 4.995 um)

classclasses.Outputs[source]
Bases: object

output data from radiative transfer calculations.

heat_rt
heating rate in each layer

BBAVIS
broadband albedo in visible range

BBANIR
broadband albedo in NIR range

BBA
broadband albedo across solar spectrum

abs_slr_btm
absorbed solar energy at bottom surface

abs_vis_btm
absorbed visible energy at bottom surface

abs_nir_btm
absorbed NIR energy at bottom surface

albedo
albedo of ice column

total_insolation
energy arriving from atmosphere

abs_slr_tot
total absorbed energy across solar spectrum

abs_vis_tot
total absorbed energy across visible spectrum

abs_nir_tot
total absorbed energy across NIR spectrum

absorbed_flux_per_layer
total absorbed flux per layer

classclasses.PlotConfig(input_file)[source]
Bases: object

Configuration for plotting figures.

figsize
size of figure

facecolor
colour of background

grid
toggles grid visibility

grid_color
color of grid lines

xtick_width
frequency of xticks

xtick_size
size of ticks on x axis

ytick_width
frequency of yticks

ytick_size
size of ticks on y axis

linewidth
pixel width of line on plot

fontsize
size of text labels

xtick_btm
toggles tick positions

ytick_left
toggle ytick position

show
toggles showing plot on screen

save
toggles saving figure to file

classclasses.RTConfig(input_file)[source]
Bases: object

Radiative transfer configuration.

aprx_type
choice of two-stream approximation (0-2)

delta
Boolean to toggle delta transformation (0/1)

biosnicar.column_OPs module
biosnicar.display module
display.calculate_band_ratios(albedo)[source]
display.display_out_data(outputs)[source]
display.plot_albedo(plot_config, model_config, albedo)[source]
display.setup_axes(plot_config)[source]
biosnicar.geometric_optics_ice module
Calculates optical properties of large hexagonal ice grains.

This file calculates the optial properties (single scattering albedo, assymetry parameter, mass absorption coefficient and extinction, scattering and absorption cross sections) for ice grains shaped as arbitrarily large hexagonal plates or columns. The optical propertiesare then saved into netCDF files in the correct format for loading into BioSNICAR.

The main function calc_optical_params() is based upon the equations of Diedenhoven et al (2014) who provided a python script as supplementary material for their paper. The original code can be downloaded from: https://www.researchgate.net/publication/259821840_ice_OP_parameterization

The optical properties are calculated using a parameterization of geometric optics calculations (Macke et al., JAS, 1996).

There are no user defined inputs for the preprocessing function, it can simply be run as

reals, imags, wavelengths = preprocess()

The calc_optical_params() fnction takes several inputs. reals, imags and wavelengths are output by preprocess() and side_length and depth are user defined. These are the two parameters that control the dimensions of the ice crystals. Side_length is the length in microns of one side of the hexagnal face of the crystal, depth is the column length also in microns describing the z dimension. The code then calculates volume, apotherm, aspect ratio, area etc inside the function. The optical parameters are returned. Optional plots and printed values for the optical params are provided by setting plots to true and the dimensions of the crystals can be reported by setting report_dims to true in the function call.

The final function, net_cdf_updater() is used to dump the optical parameters and metadata into a netcdf file and save it into the working directory to be used as a lookup library for the two-stream radiative transfer model BoSNICAR_GO.

The function calls are provided at the bottom of this script in a loop, where the user can define the range of side lengths and depths to be looped over.

NOTE: The extinction coefficient in the current implementation is 2 for all size parameters as assumed in the conventional geometric optics approximation.

geometric_optics_ice.calc_optical_params(side_length, depth, reals, imags, wavelengths, plots=False, report_dims=False)[source]
Calculates single scattering optical properties.

Van Diedenhoven’s parameterisation is used to calculate the single scatterign optical properties of hexagonal ice columns of given dimensions.

Parameters
side_length – length of side of hexagonal face (um)

depth – length of hexagonal column (um)

reals – numpy array of real parts of RI by wavelength

imags – numpy array of imaginary parts of RI by wavelength

wavelengths – numpy array of wavelenmgths (um)

plots – Boolean to toggle plotting OPs

report_dims – Boolean to toggle printing OP data to terminal

Returns
g_list – assymetry parameter

ssa_list – single scattering albedo

mac_list – mass absorption coefficient

depth – length of hexagional column (um)

side_length – length of side of hexagonal face (um)

diameter – diameter across hexaginal face.

geometric_optics_ice.net_cdf_updater(ri_source, savepath, g_list, ssa_list, mac_list, depth, side_length, density)[source]
Updates a template NetCDF file with new OP data.

Parameters
ri_source – chocie of refractive index file

savepath – path to save output data

g_list – asymmetry parameter

ssa_list – single scattering albedo

mac_list – mass absorption coefficient

depth – length of hexagional column (um)

side_length – length of side of hexagonal face (um)

density – density of material in kg/m3.

Returns
None but saves NetCDF file to savepath

geometric_optics_ice.preprocess_RI(ri_source, path_to_ri)[source]
Preprocessing of wavelength and RI data.

Preprocessing function that ensures the wavelengths and real/imaginary parts of the refractive index for ice is provided in the correct waveband and correct spectral resolution to interface with BioSNICAR. The refractive indices are taken from Warren and Brandt 2008.

Grabs appropriates wavelengths, real and imaginary parts of ice refractive index. The source of the refractive index data is controlled by var “ri_source” where 0 = Warren 1984, 1 = Warren 2008 and 2 = Picard 2016.

These are then passed as numpy arrays to the Geometrical Optics function.

Parameters
ri_source – choice of refractive index

path_to_ri – path to directory containing RI data

Returns
reals – numpy array of real parts of RI by wavelength

imags – numpy array of imaginary parts of RI by wavelength

wavelengths – numpy array of wavelengths (um)

biosnicar.mie_coated_water_spheres module
Copyright (C) 2020 Niklas Bohn (GFZ, <nbohn@gfz-potsdam.de>), German Research Centre for Geosciences (GFZ, <https://www.gfz-potsdam.de>)

mie_coated_water_spheres.fill_nans_scipy1(padata, pkind='nearest')[source]
Interpolates data to fill nan values.

Args: padata: source data with np.NaN values pkind: kind of interpolation (see scipy.interpolate.interp1d docs)

Returns
f (aindexes) – data with interpolated values instead of nans

mie_coated_water_spheres.miecoated(m1, m2, x, y)[source]
Mie Efficiencies of coated spheres.

Calculates Mie efficiencies for given complex refractive-index ratios m1=m1’+im1”, m2= m2’+im2” of kernel and coating, resp., and size parameters x=k0*a, y=k0*b where k0 = wave number in ambient medium, a,b = inner, outer sphere radius, using complex Mie Coefficients an and bn for n=1 to nmax, s. Bohren and Huffman (1983) BEWI:TDD122, p. 181-185,483.

opt selects the function “Miecoated_ab..” for an and bn, n=1 to nmax.

Note that 0<=x<=y (Matzler, 2002).

Parameters
m1 – refractive-index ratio of kernel

m2 – refractive-index ratio of coating

x – size parameter for inner sphere

y – size parameter for outer sphere

Returns
qext – extinction efficiency

qsca – scatterign efficiency

qb – backscattering efficiency

asy – asymmetry parameter

qratio – qb/qsca

mie_coated_water_spheres.miecoated_ab3(m1, m2, x, y)[source]
Computation of Mie Coefficients.

Computes a_n, b_n, of orders n=1 to nmax, complex refractive index m=m’+im”, and size parameters x=k0*a, y=k0*b where k0 = wave number in the ambient medium for coated spheres, a = inner radius, b = outer radius m1, m2 = inner, outer refractive index;

p. 183 in Bohren and Huffman (1983) BEWI:TDD122 but using the bottom equation on p. 483 for chi_prime (Matzler 2002).

Parameters
m1 – refractive index for inner sphere

m2 – refractive index for outher sphere

x – size parameter for inner sphere

y – size parameter for outer sphere

Returns
Mie Coefficients a_n and b_n

mie_coated_water_spheres.miecoated_driver(rice, rwater, fn_ice, rf_ice, fn_water, wvl)[source]
Driver for miecoated.

Originally written by Christian Matzler (see Matzler, 2002). The driver convolves the efficiency factors with the particle dimensions to return the cross sections for extinction, scattering and absorption plus the asymmetry parameter, q ratio and single scattering albedo.

Note that the code includes an interpolation regime. This is because the original code produced NaNs for a few wavelengths at certain size parameters, particularly in the mid NIR wavelengths.

Adapted from Matlab code by Joseph Cook, University of Sheffield, UK (2017).

Parameters
rice – inner sphere diameter in microns

rwater – outer sphere diameter in microns (i.e. total coated sphere, not water layer thickness)

fn_ice – path to csv file containing refractive index of ice (Warren, 1984)

fn_water – path to csv file containing refractive index of liquid water (Segelstein, 1981)

wvl – wavelength which should be calculated (in microns)

Returns – res: tuple containing cross sections for extinction, scattering and absorption plus the asymmetry parameter, q ratio and single scattering albedo

biosnicar.setup_snicar module
biosnicar.toon_rt_solver module
biosnicar.validate_inputs module
validate_inputs.validate_glacier_algae(impurities)[source]
Validates snow algae configuration. This includes warning the user that OPs are from literature and not yet field validated. Most importantly, checks that the units of the absorption coefficient and the cell concentration match up (m2/cell -> cells/mL, m2/mg -> ppb)

Parameters
impurities – a list of Impurity objects

Returns
None

Raises
ValueError when units mismatch –

validate_inputs.validate_ice(ice)[source]
Validates ice configuration.

Parameters
ice – a class containing ice physical constants

Returns
None

Raises
ValueError when lengths of variables are not equal –

validate_inputs.validate_illumination(illumination)[source]
Validates illumination.

Parameters
illumination – a list of Impurity objects

Returns
None

Raises
ValueError when SZA or nbr_wvl outside valid range –

validate_inputs.validate_inputs(ice, rt_config, model_config, illumination, impurities)[source]
Checks all config to make sure all inputs are valid by calling out to: validate_snow_algae() validate_ilumination() validate_ice()

Parameters
ice – instance of Ice class

rt_config – instance of RTConfig class

model_config – instance of ModelConfig class

illumination – instance of Illumination class

impurities – list of instances of Impurity class

Returns
None

validate_inputs.validate_model_config(model_config)[source]
Validates model configuration.

Parameters
model_config – a class containing model config variables

Returns
None

Raises
ValueError when wavelengths are incorrect –

validate_inputs.validate_snow_algae(impurities)[source]
Validates snow algae configuration. This includes warning the user that OPs are from literature and not yet field validated. Most importantly, checks that the units of the absorption coefficient and the cell concentration match up (m2/cell -> cells/mL, m2/mg -> ppb)

Parameters
impurities – a list of Impurity objects

Returns
None

Raises
ValueError when units mismatch –