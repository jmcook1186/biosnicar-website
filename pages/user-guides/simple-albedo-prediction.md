# Predicting albedo

The main use case for `biosnicar` is to predict the albedo of a snow and/or ice surface given a set of values desribing the physical configuration of the ice column, any particles in/on it and the illumination conditions.

When you download `biosnicar` it is all set up for this use case. You can simply run the following command from your terminal to generate a spectral albedo with all the default settings:

```sh
python src/biosnicar/main.py
```

Once you have tried this and seen `biosnicar` work, you can start creating your own configurations and simulating specific environments. All the values you might want to change are set in a single file: `inputs.yaml`.

To see an explanation of each value, visit the [Inputs page](../guides/inputs.mdx).

You can simply update the values in this file, save it, and then run the driver script again.

## Updating the driver script

You can write your own driver script. We have provided a default `main.py` as an example that you can use, but you can be creative and run the `biosnicar` functions however you see fit. We wrapped everything you need into a single function, `get_albedo` so all you have to do is call that function. The `get_albedo()` function takes three simple arguments. First, decide which radiative transfer solver you want to use and pass the name (either `"toon"` or `"adding-doubling"`) as the first argument. Then, you can toggle albedo plotting on/off by passing `plot=True` or `plot=False`. You can also choose whether you want `biosnicar` to check your input values are valid - this can help prevent accidentally creating unrealistic model scenarios, but if you toggle it off you will benefit from a (small) increase in execution speed. Pass `validation=True` or `validation=False` to configure the function. That's all you need to do - everything else is automated and `biosnicar` will pull the remaining configuration from `inputs.yaml`.

To customize your `biosnicar` runs further, you can use the individual `biosnicar` functions instead of the convenience wrappers. The `get_albedo()` wrapper is executing the following steps in this order:

- import the biosnicar modules
- provide the path to `inputs.yaml`
- instantiate the necessary classes by calling `setup_snicar()`
- get the ice column optical properties by calling `get_layer_OPs()` and `mix_in_impurities()`
- solve the radiative transfer equations by calling either `adding_doubling_solver()` or `toon_solver`
- you probably also want to plot the albedo using `plot_albedo()`

Here's a minimal example:

```py
from pathlib import Path
from biosnicar.adding_doubling_solver import adding_doubling_solver
from biosnicar.column_OPs import get_layer_OPs, mix_in_impurities
from biosnicar.display import display_out_data, plot_albedo
from biosnicar.setup_snicar import setup_snicar
from biosnicar.toon_rt_solver import toon_solver
from biosnicar.validate_inputs import validate_inputs

(
    ice,
    illumination,
    rt_config,
    model_config,
    plot_config,
    impurities,
) = setup_snicar()

# now get the optical properties of the ice column
ssa_snw, g_snw, mac_snw = get_layer_OPs(ice, model_config)
tau, ssa, g, L_snw = mix_in_impurities(
    ssa_snw, g_snw, mac_snw, ice, impurities, model_config
)
# now run one or both of the radiative transfer solvers
outputs1 = adding_doubling_solver(tau, ssa, g, L_snw, ice, illumination, model_config)
plot_albedo(plot_config, model_config, outputs1.albedo)
```

You could save this as `example.py`, save it in `src/biosnicar` and run from the project directory using:

```sh
python src/biosnicar/example.py
```

Using this sequence of function calls instead of the `get_albedo()` wrapper gives you access to the return values of all the intermediate functions, such as the physical and optical properties of the ice column. You also get the full set of output values so you can decide what to plot, download or pass into some new logic you create for yourself!

We have made `biosnicar` as composable as possible, so you can tailor the complexity to your needs. You can chop up and recompose elements of `biosnicar` in creative ways to go beyond simple albedo predictions!