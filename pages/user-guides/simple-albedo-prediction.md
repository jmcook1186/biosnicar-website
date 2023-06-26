# Predicting albedo

The main use case for `biosnicar` is to predict the albedo of a snow and/or ice surface given a set of values desribing the physical configuration of the ice column, any particles in/on it and the illumination conditions.

When you download `biosnicar` it is all set up for this use case. You can simply run the following command from your terminal to generate a spectral albedo with all the default settings:

```sh
python src/biosnicar/snicar_driver.py
```

Once you have tried this and seen `biosnicar` work, you can start creating your own configurations and simulating specific environments. All the values you might want to change are set in a single file: `inputs.yaml`.

To see an explanation of each value, visit the [Inputs page](../guides/inputs.mdx).

You can simply update the values in this file, save it, and then run the driver script again.

## Updating the driver script

You can write your own driver script. We have provided `snicar_driver.py` as an example that you can use as a template, but you can be creative and run the `biosnicar` functions however you see fit. We wrapped all the prerequisite setup into a single function, `setup_snicar()` for convenience.

To get an albedo prediction, the following steps are required:

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

BIOSNICAR_SRC_PATH = Path(__file__).resolve().parent
# define input file
INPUT_FILE = BIOSNICAR_SRC_PATH.joinpath("inputs.yaml").as_posix()
# first build classes from config file and validate their contents
(
    ice,
    illumination,
    rt_config,
    model_config,
    plot_config,
    impurities,
) = setup_snicar(INPUT_FILE)

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

## Why not just have one function?

It has been asked in the past why it is necessary to run multiple functions in sequence just to get an albedo value, rather than just wrapping all the logic in a single `get_albedo()` function. It might be a nice feature to eventually add a wrapper around all the above functions so that albedo can be generated in a single function call. However, at the moment we feel it is overall beneficial to have the logic separated with one outcome per function. This is to make it as easy as possible to split up the logic and use `biosnicar` in creative ways. For example, to extract intermediate values (say, the ice optical properties) it is a simple case of using the values returned from `get_layer_OPs()` or `mix_in_impurities()` rather than having to modify some monolithic codebase and worry about unintended side-effects.