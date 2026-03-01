# Outputting values other than albedo

Albedo predictions are the most common use case for `biosnicar`. However, the model can return a wide range of different values.
This already happens in the downloaded version of `biosnicar` - you don't have to do anything to enable it. The outputs from the radiative transfer solver, either adding-doubling or Toon, comes in the form of an instance of an `Outputs` class. This object has the following fields:

- `albedo`: Spectral albedo
- `BBA`: Broadband albedo calculated from `albedo`
- `BBAVIS`: Broadband albedo in the visible wavelengths only
- `BBANIR`: Broadband albedo in the near-infrared wavelengths only
- `total_insolation`: Total energy received at the surface in W/m^2
- `abs_slr_btm`: Spectrally-integrated absorption by underlying surface
- `abs_vis_btm`: Spectrally-integrated absorption by underlying surface in the visible wavelengths only
- `abs_nir_btm`: Spectrally-integrated absorption by underlying surface in the near infrared wavelengths only
- `abs_slr_tot`: Spectrally-integrated VIS and NIR total column absorption
- `abs_vis_tot`: Spectrally-integrated VIS and NIR total column absorption in the visible wavelengths only
- `abs_nir_tot`: Spectrally-integrated VIS and NIR total column absorption in the near infrared wavelengths only
- `absorbed_flux_per_layer`: energy absorbed in each vertical layer
- `heat_rt`: Radiative heating rate in K/hr

It is also possible to extend the scope of `Outputs` to include some more values that are currently treated as intermediates in the radiative transfer model. For example, upwards and downward fluxes in each layer (output from the `calculate_fluxes()` function in each solver but not propagated to `Outputs`).

## Using `run_model()` (recommended)

The `run_model()` function already returns the full `Outputs` object, giving you access to all the fields listed above:

```py
from biosnicar.drivers.run_model import run_model

outputs = run_model(solzen=50, rds=1000)

print(outputs.albedo)    # spectral albedo (480 wavelengths)
print(outputs.BBA)       # broadband albedo
print(outputs.BBAVIS)    # visible broadband albedo
print(outputs.BBANIR)    # NIR broadband albedo
print(outputs.heat_rt)   # heating rate
print(outputs.absorbed_flux_per_layer)  # absorbed energy per layer
```

## Using `get_albedo()` wrapper

**Note** that the `get_albedo()` convenience wrapper returns only the spectral albedo array — not the full `Outputs` object. If you need other output values, use `run_model()` instead.

## Using individual functions

For maximum control, you can also run the individual `biosnicar` functions without any wrapper:

```py
from biosnicar.rt_solvers.adding_doubling_solver import adding_doubling_solver
from biosnicar.optical_properties.column_OPs import get_layer_OPs, mix_in_impurities
from biosnicar.utils.display import display_out_data, plot_albedo
from biosnicar.drivers.setup_snicar import setup_snicar

(
    ice,
    illumination,
    rt_config,
    model_config,
    plot_config,
    impurities,
) = setup_snicar("default")

# now get the optical properties of the ice column
ssa_snw, g_snw, mac_snw = get_layer_OPs(ice, model_config)
tau, ssa, g, L_snw = mix_in_impurities(
    ssa_snw, g_snw, mac_snw, ice, impurities, model_config
)
# now run one or both of the radiative transfer solvers
outputs = adding_doubling_solver(tau, ssa, g, L_snw, ice, illumination, model_config)

# now you have access to all the output values. You can access them for plotting or
# printing, or using in some other way.

plot_albedo(plot_config, model_config, outputs.albedo) # plot albedo
print(outputs.BBA) # print broadband albedo

```
