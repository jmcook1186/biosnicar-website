# Predicting albedo

The main use case for `biosnicar` is to predict the albedo of a snow and/or ice surface given a set of values desribing the physical configuration of the ice column, any particles in/on it and the illumination conditions.

When you download `biosnicar` it is all set up for this use case. You can simply run the following command from your terminal to generate a spectral albedo with all the default settings:

```sh
python main.py
```

Once you have tried this and seen `biosnicar` work, you can start creating your own configurations and simulating specific environments. All the values you might want to change are set in a single file: `inputs.yaml`.

To see an explanation of each value, visit the [Inputs page](../guides/inputs.mdx).

You can simply update the values in this file, save it, and then run the driver script again.

## Using `run_model()` (recommended)

The recommended way to run `biosnicar` programmatically is with the `run_model()` function. It handles the full pipeline (setup, optical properties, impurity mixing, radiative transfer) in a single call and accepts keyword overrides for any model parameter:

```py
from biosnicar.drivers.run_model import run_model

# Run with all defaults from inputs.yaml
outputs = run_model()
print(outputs.BBA)       # broadband albedo
print(outputs.albedo)    # 480-element spectral albedo

# Override specific parameters
outputs = run_model(solzen=50, rds=1000, impurity_0_conc=500)
print(outputs.BBA)
```

`run_model()` is also accessible as `biosnicar.run_model()` after `import biosnicar`.

Supported override keys include `solzen`, `direct`, `incoming`, `rds`, `rho`, `dz`, `lwc`, `layer_type`, and `impurity_{i}_conc` (where `i` is the 0-based impurity index). Scalar values for ice parameters are broadcast to all layers; scalar impurity concentrations are applied to the first layer only.

You can also toggle input validation and plotting:

```py
outputs = run_model(solver="adding-doubling", validate=True, plot=True, solzen=60)
```

## Using `get_albedo()` wrapper

The `get_albedo()` wrapper is a thin convenience function around `run_model()` that returns only the spectral albedo array. It takes three simple arguments: the solver name (`"toon"` or `"adding-doubling"`), `plot=True/False`, and `validate=True/False`:

```py
from biosnicar.drivers import get_albedo

albedo = get_albedo.get("adding-doubling", plot=True, validate=True)
```

## Using individual functions

For maximum control, you can call the individual `biosnicar` functions directly. This gives you access to the return values of all the intermediate functions, such as the physical and optical properties of the ice column:

```py
from biosnicar.rt_solvers.adding_doubling_solver import adding_doubling_solver
from biosnicar.optical_properties.column_OPs import get_layer_OPs, mix_in_impurities
from biosnicar.utils.display import display_out_data, plot_albedo
from biosnicar.drivers.setup_snicar import setup_snicar
from biosnicar.rt_solvers.toon_rt_solver import toon_solver

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
outputs1 = adding_doubling_solver(tau, ssa, g, L_snw, ice, illumination, model_config)
plot_albedo(plot_config, model_config, outputs1.albedo)
```

You could save this as `example.py`, save it in the project directory and run using:

```sh
python example.py
```

Using this sequence of function calls instead of `run_model()` gives you access to the return values of all the intermediate functions, such as the physical and optical properties of the ice column. You also get the full set of output values so you can decide what to plot, download or pass into some new logic you create for yourself!

We have made `biosnicar` as composable as possible, so you can tailor the complexity to your needs. You can chop up and recompose elements of `biosnicar` in creative ways to go beyond simple albedo predictions!
