# Built-in Emulator

BioSNICAR includes a built-in neural-network emulator that replaces the full radiative transfer solver with a fast surrogate model. Once trained, the emulator predicts spectral albedo in **microseconds** instead of the ~50 ms required by the full forward model — a speedup of several orders of magnitude. This makes tasks that require thousands of model evaluations (optimisation, MCMC, sensitivity analysis) practical in seconds rather than hours.

## Why use an emulator?

The full BioSNICAR forward model solves the radiative transfer equation layer-by-layer at 480 wavelengths. Each evaluation takes ~50 ms, which is fine for a single run but becomes a bottleneck when you need many evaluations:

| Task | Evaluations | Forward model | Emulator |
|------|-------------|---------------|----------|
| Single prediction | 1 | 50 ms | ~1 µs |
| L-BFGS-B retrieval | ~2,000 | ~100 s | <1 s |
| Parameter sweep (1000 points) | 1,000 | ~50 s | ~1 ms |
| MCMC (32 walkers x 5000 steps) | 160,000 | ~2.2 hours | ~1 min |

The emulator also produces **smooth, differentiable** output, which is essential for gradient-based optimisers like L-BFGS-B. The full solver's output can have minor numerical noise that confuses gradient estimation.

## Quick start

### Using the default emulator

BioSNICAR ships with a pre-built 8-parameter default emulator trained on 50,000 forward model runs for glacier ice:

```py
from biosnicar.emulator import Emulator

emu = Emulator.load("data/emulators/glacier_ice_8_param_default.npz")

# Single prediction (microseconds)
albedo = emu.predict(rds=1000, rho=600, black_carbon=5000, solzen=50, direct=1)
print(albedo.shape)  # (480,)

# Or use the run_emulator wrapper for an Outputs object
from biosnicar import run_emulator

outputs = run_emulator(emu, rds=1000, rho=600, black_carbon=5000, solzen=50, direct=1)
print(outputs.BBA)          # broadband albedo
print(outputs.to_platform("sentinel2"))  # satellite bands work too
```

The default emulator covers these parameters:

| Parameter | Range | Units |
|-----------|-------|-------|
| `rds` | 500 -- 10,000 | um |
| `rho` | 300 -- 900 | kg/m3 |
| `black_carbon` | 0 -- 5,000 | ppb |
| `snow_algae` | 0 -- 500,000 | cells/mL |
| `glacier_algae` | 0 -- 500,000 | cells/mL |
| `dust` | 0 -- 50,000 | ppb |
| `direct` | 0 -- 1 | binary |
| `solzen` | 25 -- 80 | degrees |

### Building a custom emulator

If the default parameter ranges don't suit your application, build your own:

```py
from biosnicar.emulator import Emulator

emu = Emulator.build(
    params={
        "rds": (100, 5000),
        "black_carbon": (0, 100000),
        "glacier_algae": (0, 500000),
    },
    n_samples=5000,       # training samples
    layer_type=1,         # fixed: solid ice
    solzen=50,            # fixed solar zenith angle
    direct=1,             # fixed: clear sky
    progress=True,        # show progress bar
    seed=42,
)
```

Parameters listed in `params` are **free** (the emulator learns their effect). All other keyword arguments are **fixed** constants used for every training run. Any keyword accepted by `run_model()` can be used.

### Save and load

Emulators save as compact `.npz` files (~100-200 KB) that require only NumPy to load — no scikit-learn or other ML libraries needed at inference time:

```py
emu.save("my_emulator.npz")

# Later, or on a different machine:
emu2 = Emulator.load("my_emulator.npz")
```

## How it works

The build process has five stages:

1. **Latin Hypercube Sampling** generates training points that fill the parameter space uniformly. Impurity concentrations are sampled in log10(x+1) space to ensure adequate coverage of clean-ice scenarios alongside high-loading ones.

2. **Forward model evaluation** runs BioSNICAR at each sample point to produce a 480-band spectral albedo. This is the time-consuming step (~50 ms per sample).

3. **Filtering** removes any spectra with unphysical values (negative albedo or values exceeding 1.01) that occasionally arise from numerical instability at extreme parameter combinations.

4. **PCA compression** reduces the 480-band spectra to ~10 principal components, capturing >99.9% of spectral variance. This regularises the training (the network learns smooth spectral structure, not noise) and dramatically reduces the network size.

5. **MLP training** fits a small neural network (128-128-64 hidden units, ReLU activation) to map input parameters to PCA coefficients. Training uses scikit-learn's `MLPRegressor` with early stopping.

At inference time, prediction is a pure NumPy forward pass: input scaling, four matrix multiplications, and PCA reconstruction. No ML framework is needed.

### Why an MLP?

We evaluated several alternatives:

- **Gaussian Processes**: O(n^3) scaling makes them impractical beyond a few thousand training points.
- **Random Forest / XGBoost**: Produces step-function approximations that are not differentiable, breaking gradient-based optimisers.
- **Polynomial regression**: Cannot capture the nonlinear spectral features of ice albedo.
- **MLP**: O(N) inference, microsecond predictions, smooth differentiable output, and compact storage (~100 KB). The sweet spot for this problem.

## Verifying accuracy

Always verify a new emulator before using it for retrieval:

```py
result = emu.verify(n_points=100, seed=123)
print(result.summary())
```

This runs the full forward model at random parameter combinations and compares against emulator predictions. Expect:

- Spectral MAE: < 0.005 (0.5% absolute error)
- BBA MAE: < 0.005
- R2: > 0.999

## Batch predictions

For parameter sweeps or sensitivity analysis, `predict_batch()` processes many parameter sets at once:

```py
import numpy as np

points = np.array([
    [1000, 600, 5000],   # rds, rho, black_carbon
    [2000, 700, 10000],
    [3000, 800, 0],
])

batch = emu.predict_batch(points)
print(batch.shape)  # (3, 480)
```

## Integration with inversions

The emulator integrates directly with the [inversion module](/user-guides/model-inversions), providing the fast forward evaluations needed for optimisation and MCMC:

```py
from biosnicar.inverse import retrieve

result = retrieve(
    observed=measured_spectrum,
    parameters=["ssa", "black_carbon"],
    emulator=emu,
    fixed_params={"direct": 1, "solzen": 50, "dust": 1000},
)
```

See the [inversions guide](/user-guides/model-inversions) for full details.

## Training guidelines

| Samples | Build time | File size | Best for |
|---------|-----------|-----------|----------|
| 5,000 | ~4 min | ~100 KB | 2-3 free parameters |
| 10,000 | ~8 min | ~150 KB | 4-5 free parameters |
| 20,000 | ~17 min | ~200 KB | High-accuracy applications |

More free parameters require more training samples to fill the higher-dimensional space. As a rule of thumb, use at least 1,000 samples per free parameter.

## Limitations

- **No extrapolation**: The emulator clips inputs to the training bounds and warns if out of range. Results at the boundaries are less accurate than in the interior.
- **Single-layer only**: The default emulator treats the ice column as a single homogeneous layer. For multi-layer configurations, build a custom emulator with appropriate fixed layer parameters, or use the full forward model.
- **No subsurface fields**: The emulator predicts spectral albedo only. Heating rates, absorbed flux per layer, and subsurface light fields (`F_up`, `F_dwn`) are not available from emulator predictions — use the full forward model via `run_model()` for those.
- **PCA artefacts**: Very extreme parameter combinations near the training bounds may produce small spectral oscillations. Increasing `n_samples` mitigates this.
