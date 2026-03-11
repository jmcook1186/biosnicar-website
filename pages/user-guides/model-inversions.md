# Model Inversions

The default way to run BioSNICAR is in **forward mode**: provide ice properties, get spectral albedo. The **inverse problem** is the opposite: given an observed albedo spectrum (from a spectroradiometer or satellite), determine what ice properties produced it. BioSNICAR includes a dedicated inversion module that solves this problem using emulator-powered optimisation.

## Why inversions matter

Field and remote sensing campaigns routinely collect albedo measurements, but the physical properties of interest — grain size, impurity loading, density — cannot be measured directly at scale. Inversion bridges this gap: you provide your measurements, fix the parameters you know (solar zenith angle, sky conditions), and let BioSNICAR retrieve the unknowns.

Typical use cases:

- **Retrieve specific surface area (SSA)** from a spectroradiometer measurement
- **Estimate impurity loading** (black carbon, algae) from satellite imagery
- **Quantify uncertainty** on retrieved parameters using Bayesian methods
- **Validate field measurements** against model predictions

## Quick start

```py
from biosnicar.emulator import Emulator
from biosnicar.inverse import retrieve

# Load the default emulator
emu = Emulator.load("data/emulators/glacier_ice_8_param_default.npz")

# Create a synthetic observation (in practice, use your measurements)
observed = emu.predict(rds=1500, rho=600, black_carbon=8000, solzen=50, direct=1)

# Retrieve SSA and black carbon
result = retrieve(
    observed=observed,
    parameters=["ssa", "black_carbon"],
    emulator=emu,
    fixed_params={"direct": 1, "solzen": 50, "dust": 1000, "snow_algae": 0, "glacier_algae": 0},
)

print(f"SSA: {result.best_fit['ssa']:.2f} +/- {result.uncertainty['ssa']:.2f} m2/kg")
print(f"BC:  {result.best_fit['black_carbon']:.0f} +/- {result.uncertainty['black_carbon']:.0f} ppb")
```

## The SSA advantage

Ice albedo in the NIR is controlled by **specific surface area (SSA)**, not by bubble radius (`rds`) or density (`rho`) individually. Different (rds, rho) combinations that share the same SSA produce nearly identical spectra. This creates a degeneracy that makes direct (rds, rho) retrieval unreliable:

| Retrieved parameter | Typical error |
|---------------------|---------------|
| rds alone | ~73% |
| rho alone | ~33% |
| **SSA** | **~5.5%** |

The inversion module handles this elegantly: when you retrieve `"ssa"`, it internally decomposes SSA into (rds, rho) for each emulator call using a reference density. You get a physically meaningful result with tight uncertainty bounds.

```py
# Retrieve SSA (recommended)
result = retrieve(
    observed=spectrum,
    parameters=["ssa", "black_carbon", "glacier_algae"],
    emulator=emu,
    fixed_params={"direct": 1, "solzen": 50},
)

# The result includes the internal decomposition
print(result.derived)  # {"rds_internal": ..., "rho_ref": ...}
```

Note: you cannot retrieve `"ssa"` alongside `"rds"` or `"rho"` — SSA replaces both.

## Spectral vs satellite band modes

The inversion module supports two observation types:

### Spectral mode (480 bands)

Use this when you have hyperspectral measurements from a field spectroradiometer. The full 480-band spectrum provides maximum constraint on retrieved parameters.

```py
result = retrieve(
    observed=spectral_albedo,          # shape (480,)
    parameters=["ssa", "black_carbon"],
    emulator=emu,
    fixed_params={"direct": 1, "solzen": 50},
)
```

You can mask out noisy or unreliable wavelength regions:

```py
import numpy as np

# Only use 0.35-1.4 um (exclude UV noise and deep absorption bands)
wavelengths = np.arange(0.205, 4.999, 0.01)
mask = (wavelengths >= 0.35) & (wavelengths <= 1.4)

result = retrieve(
    observed=spectral_albedo,
    parameters=["ssa", "black_carbon"],
    emulator=emu,
    wavelength_mask=mask,
    fixed_params={"direct": 1, "solzen": 50},
)
```

### Band mode (satellite observations)

Use this when you have broadband observations from Sentinel-2, Landsat 8, MODIS, or another supported platform. The inversion convolves each candidate spectrum onto the satellite bands internally using BioSNICAR's [band convolution](/user-guides/band-ratios) module.

```py
result = retrieve(
    observed=np.array([0.82, 0.78, 0.75, 0.45, 0.03]),
    parameters=["ssa", "black_carbon"],
    emulator=emu,
    platform="sentinel2",
    observed_band_names=["B2", "B3", "B4", "B8", "B11"],
    obs_uncertainty=np.array([0.02, 0.02, 0.02, 0.03, 0.05]),
    fixed_params={"direct": 1, "solzen": 50, "dust": 1000},
)
```

Band mode has fewer observations (typically 4-5 bands), so it constrains fewer free parameters. Best practice: fix poorly-constrained parameters (dust, sky conditions) via `fixed_params` and limit free parameters to SSA plus one or two impurities.

## Optimisation methods

The `method` argument selects the optimisation algorithm. Each has different strengths:

### L-BFGS-B (default)

A hybrid two-phase strategy that combines global exploration with local polishing:

1. **Phase 1**: Quick differential evolution (DE) pre-search to escape local minima
2. **Phase 2**: L-BFGS-B gradient descent for machine-precision convergence

This is the recommended default — fast (~1-2 seconds with emulator) and robust.

```py
result = retrieve(
    observed=spectrum,
    parameters=["ssa", "black_carbon"],
    emulator=emu,
    method="L-BFGS-B",
    fixed_params={"direct": 1, "solzen": 50},
)
```

### Nelder-Mead

A derivative-free simplex method. Useful when the cost surface is noisy or non-smooth.

```py
result = retrieve(..., method="Nelder-Mead")
```

### Differential evolution

A global stochastic search. More evaluations than L-BFGS-B but thoroughly explores the parameter space. Good when you have no prior estimate for the parameters.

```py
result = retrieve(..., method="differential_evolution")
```

### MCMC (Markov Chain Monte Carlo)

Full Bayesian posterior sampling using `emcee`. Returns the complete posterior distribution, not just a point estimate. Essential for publication-quality uncertainty estimates and understanding parameter correlations.

```py
result = retrieve(
    observed=spectrum,
    parameters=["ssa", "black_carbon", "glacier_algae"],
    emulator=emu,
    method="mcmc",
    mcmc_walkers=32,
    mcmc_steps=5000,
    mcmc_burn=1000,
    fixed_params={"direct": 1, "solzen": 50},
)

# Full posterior chains for corner plots
print(result.chains.shape)           # (5000, 32, 3)
print(result.acceptance_fraction)    # target: 0.2-0.5
```

MCMC requires the `emcee` package and is significantly slower than the other methods (~30-60 seconds with the emulator), but it is the only method that provides full posterior distributions and reveals parameter correlations.

### Method comparison

| Method | Evaluations | Time (emulator) | Best for |
|--------|-------------|-----------------|----------|
| L-BFGS-B | ~2,000 | ~1 s | Default, fast and accurate |
| Nelder-Mead | ~500 | ~0.5 s | Noisy cost surfaces |
| Differential evolution | ~3,000 | ~3 s | Global search, poor initial guess |
| MCMC | ~160,000 | ~60 s | Full uncertainty, correlations |

## Observation uncertainty

Weight your observations by measurement uncertainty to prevent noisy bands from dominating the fit:

```py
result = retrieve(
    observed=spectrum,
    parameters=["ssa", "black_carbon"],
    emulator=emu,
    obs_uncertainty=uncertainty_array,   # same shape as observed
    fixed_params={"direct": 1, "solzen": 50},
)
```

The cost function becomes a chi-squared: `J = sum((predicted - observed)^2 / sigma^2)`, giving less weight to uncertain measurements.

## Regularisation (prior information)

If you have prior knowledge about a parameter (e.g. from field measurements), you can add a Gaussian regularisation term that penalises deviations from the prior:

```py
result = retrieve(
    observed=spectrum,
    parameters=["ssa", "black_carbon", "glacier_algae"],
    emulator=emu,
    regularization={
        "ssa": (5.0, 2.0),              # prior mean=5, sigma=2
        "black_carbon": (1000, 500),     # prior mean=1000, sigma=500
    },
    fixed_params={"direct": 1, "solzen": 50},
)
```

This is especially useful for weakly constrained parameters like dust concentration.

## The RetrievalResult object

The `retrieve()` function returns a `RetrievalResult` with these fields:

| Field | Type | Description |
|-------|------|-------------|
| `best_fit` | dict | Optimal parameter values |
| `uncertainty` | dict | 1-sigma uncertainty per parameter |
| `predicted_albedo` | ndarray (480,) | Spectrum at the best-fit parameters |
| `observed` | ndarray | The input observations |
| `cost` | float | Final chi-squared value |
| `converged` | bool | Whether the optimiser converged |
| `method` | str | Method used |
| `n_function_evals` | int | Number of forward evaluations |
| `derived` | dict | Internal SSA decomposition (when retrieving SSA) |
| `chains` | ndarray or None | Full MCMC posterior samples |

## Practical advice

### What to retrieve, what to fix

Not all parameters are equally well-constrained by albedo observations:

- **SSA**: Very well constrained (controls NIR albedo shape). Always retrievable.
- **Black carbon, algae**: Well constrained (control visible darkening). Retrievable when VIS bands are included.
- **Solar zenith angle**: Moderately constrained. Usually known from metadata — fix it.
- **Dust**: Poorly constrained (flat spectral signature at typical concentrations). Fix via `fixed_params` unless concentrations are very high (>10,000 ppb) or strong priors are available.
- **Direct/diffuse**: Binary parameter, not continuously optimisable. Always fix via `fixed_params`.

### Recommended workflow

1. Fix everything you know: `solzen`, `direct`, atmospheric conditions
2. Retrieve SSA (not rds/rho separately) for grain size information
3. Add one or two impurity parameters if you have VIS observations
4. Use `obs_uncertainty` if you have measurement error estimates
5. Run L-BFGS-B first for a quick answer, then MCMC if you need full uncertainty

### Using the forward model directly

If you don't want to use the emulator (e.g. for multi-layer configurations), pass a forward function instead:

```py
from biosnicar import run_model

result = retrieve(
    observed=spectrum,
    parameters=["rds", "black_carbon"],
    forward_fn=lambda **kw: run_model(**kw).albedo,
    fixed_params={"direct": 1, "solzen": 50, "rho": 600},
)
```

This is slower (~50 ms per evaluation vs microseconds for the emulator) but supports the full parameter space and multi-layer configurations.
