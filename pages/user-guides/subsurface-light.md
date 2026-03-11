# Subsurface Light Fields

BioSNICAR's radiative transfer solvers compute spectral upwelling and downwelling fluxes at every layer interface in the ice column. These arrays are exposed as first-class attributes on the `Outputs` object, together with convenience methods for depth interpolation, PAR estimation, and spectral heating rates.

This means you can now answer questions like "what is the PAR at 5 cm depth?", "how does impurity loading change the spectral irradiance profile?", or "which wavelengths dominate radiative heating in each layer?" — all without modifying solver internals.

## Why subsurface light fields matter

The spectral albedo at the surface tells you how much light is reflected, but says nothing about what happens to the light that enters the ice. For many applications, the subsurface distribution matters:

- **Photobiology**: Algae, bacteria, and photosynthetic organisms living within ice respond to the local PAR (400-700 nm irradiance), not the surface albedo. Understanding how PAR varies with depth and impurity loading is essential for modelling biological productivity on glaciers and ice sheets.

- **Radiative heating**: Ice absorbs solar energy at depth, not just at the surface. The spectral heating rate reveals which wavelengths deposit energy in which layers — critical for surface energy balance models and melt prediction.

- **Photochemistry**: Photochemical reactions in ice (e.g. NOx production, organic matter degradation) depend on the local spectral irradiance, not just the total absorbed flux.

- **Cryoconite holes**: The light field around subsurface absorbers drives differential melting. Understanding the spectral flux profile through the column helps explain how cryoconite holes form and deepen.

## Quick start

```py
from biosnicar import run_model

outputs = run_model(solzen=60, rds=500, dz=[0.01, 0.02, 0.05, 0.1, 0.82])

# Raw flux arrays at layer interfaces
print(outputs.F_dwn.shape)   # (480, 6) — 480 wavelengths, 6 interfaces

# Spectral flux at 3 cm depth (interpolated)
flux = outputs.subsurface_flux(0.03)
print(flux["F_dwn"].shape)   # (480,)

# PAR at several depths
import numpy as np
depths = np.linspace(0, 0.5, 20)
par = outputs.par(depths)
```

## Raw flux arrays

After any call to `run_model()`, the `Outputs` object carries two new arrays:

| Attribute | Shape | Description |
|-----------|-------|-------------|
| `F_up` | (480, nbr_lyr+1) | Spectral upwelling flux at each layer interface |
| `F_dwn` | (480, nbr_lyr+1) | Spectral downwelling flux at each layer interface |

Column 0 is the **surface** (top of column). Column `nbr_lyr` is the **bottom** (base of deepest layer). Both the adding-doubling and Toon solvers populate these arrays in the same convention.

**Units**: Fluxes are normalised so that total incoming irradiance sums to 1 across all 480 bands. To obtain absolute values in W/m2, multiply by the actual total incoming irradiance for your site and time.

## Interpolation at arbitrary depths

`subsurface_flux(depth_m)` returns spectral fluxes at any depth by linearly interpolating between the two bracketing layer interfaces:

```py
# Single depth
flux = outputs.subsurface_flux(0.05)
print(flux["F_up"].shape)    # (480,)
print(flux["F_dwn"].shape)   # (480,)
print(flux["F_net"].shape)   # (480,) — F_dwn - F_up

# Multiple depths at once
flux = outputs.subsurface_flux([0.0, 0.01, 0.05, 0.1, 0.5])
print(flux["F_dwn"].shape)   # (5, 480)
```

Depths are clipped to the column bounds: 0 returns the surface interface, and any depth beyond the total column thickness returns the bottom interface.

For best results, use many thin layers in your ice column so the interpolation has closely spaced interface points to work with.

## PAR at depth

`par(depth_m)` returns the Photosynthetically Active Radiation (400-700 nm) — the sum of downwelling flux across the PAR band:

```py
# Surface PAR
print(outputs.par(0.0))          # scalar

# PAR depth profile
depths = np.linspace(0, 0.5, 20)
par = outputs.par(depths)        # array of length 20
```

### Flux enhancement near the surface

You may notice that PAR (and `F_dwn` generally) at shallow sub-surface depths **exceeds** the incoming surface value. This is not a bug — it is a real physical effect called *radiation trapping*.

At the surface, `F_dwn` is purely the incoming radiation: there is no scattering medium above to redirect light back downward. At the first sub-surface interface, `F_dwn` has three components:

1. **Direct beam** transmitted through the overlying layer (slightly attenuated)
2. **Diffuse sky radiation** transmitted through the overlying layer
3. **Upwelling radiation from below** that is **scattered back downward** by the overlying layer

In the visible, ice has an extremely high single-scattering albedo (ssa ~0.99998), so component (3) — multiply-scattered light bouncing between layers — more than compensates for the small attenuation of components (1) and (2). Photons bounce many times before being absorbed, and both the upwelling and downwelling flux streams are enhanced within the medium relative to the boundary value. This is the same physics that makes deep snow glow from within when you dig a snow pit.

The enhancement is strongest in the top ~1 transport mean-free-path and diminishes with depth as absorption gradually removes energy. The **net** flux (`F_dwn - F_up`) always decreases monotonically with depth, as required by energy conservation.

The effect is most pronounced in the PAR band (400-700 nm) where ice absorption is negligible, and weaker in the NIR where absorption is much stronger.

## Spectral heating rate

`spectral_heating_rate()` returns the radiative heating rate resolved by wavelength and layer:

```py
shr = outputs.spectral_heating_rate()
print(shr.shape)  # (480, nbr_lyr)

# Broadband heating rate per layer
broadband = np.sum(shr, axis=0)
print(broadband)  # K/hr per layer
```

The calculation uses the flux divergence in each layer:

```
F_net = F_up - F_dwn
F_abs = F_net[:, 1:] - F_net[:, :-1]
heating_rate = F_abs / (L_snw * 2117) * 3600    # K/hr per band
```

where `L_snw` is the ice mass per layer (kg/m2) and 2117 is the specific heat capacity of ice (J/kg/K).

### NIR dominates heating

You might expect visible wavelengths to dominate heating since that's where most solar energy arrives. In fact, **NIR wavelengths dominate** — especially near 1.0, 1.25, and 1.5 um. The reason is ice transparency: ice is nearly transparent in the visible (absorption coefficient is negligible from 400-700 nm), so VIS photons scatter through the column without depositing much energy. In the NIR, ice absorption increases by orders of magnitude, so these wavelengths are absorbed efficiently in the upper layers and dominate the radiative heating budget.

## Worked example: clean vs algae-loaded PAR

```py
import numpy as np
from biosnicar import run_model

dz = [0.01, 0.02, 0.02, 0.05, 0.05, 0.05, 0.1, 0.1, 0.1]
rho = [400] * len(dz)

clean = run_model(solzen=50, rds=500, dz=dz, rho=rho)
algae = run_model(solzen=50, rds=500, dz=dz, rho=rho, glacier_algae=50000)

depths = np.linspace(0, 0.5, 20)
par_clean = clean.par(depths)
par_algae = algae.par(depths)

for d, pc, pa in zip(depths, par_clean, par_algae):
    print(f"  {d:.3f} m   clean={pc:.4f}   algae={pa:.4f}")
```

The algal-loaded column shows lower PAR at depth because glacier algae absorb strongly in the visible, removing photons from the PAR band before they can penetrate deeper. This is the mechanism by which biological darkening accelerates ice melt — impurities shift energy absorption towards the surface, increasing the heating rate in the upper layers.

## Limitations

- **Two-stream approximation**: The solver provides hemispheric (planar) fluxes, not angular radiance distributions. For applications requiring full angular resolution or 2-D/3-D light fields (e.g. around cryoconite holes), Monte Carlo radiative transfer codes are more appropriate.
- **Linear interpolation**: `subsurface_flux()` linearly interpolates between layer interfaces. For thick layers the within-layer profile may be exponential rather than linear. Splitting thick layers into thinner sub-layers improves accuracy.
- **Normalised fluxes**: The model normalises total incoming irradiance to 1. Multiply outputs by actual irradiance to obtain absolute W/m2 values.
- **Plane-parallel**: No lateral photon transport is modelled.
- **Not available from emulator**: Subsurface light fields require the full forward model (`run_model()`). The [emulator](/user-guides/emulator) predicts surface spectral albedo only.
