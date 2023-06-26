# Outputting values other than albedo

Albedo predictions are the most common use case for `biosnicar`. However, the model can return a wide range of different values.
This already happens in the downloaded version os `biosnicar` - you don't have to do anything to enable it. The outputs from the radiative transfer solver, either adding-doubling or Toon, comes in the form of an instance of an `Outputs` class. This object has the following fields:

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

It is also possible to extend the scope of `Outputs` to include some more values that are currently treated as intermediates in the radiative transfer model. For example, upwards and downward fluxes in each layer (output from the `calculate_fluxes()` function in each solver but not propagated to `Outputs`)