# Handling multiple runs

The default `main.py` produces a single spectral albedo prediction for a given set of input parameters. However, many users will want to run `biosnicar` many times with lots of different input values. perhaps to test the sensitivity of the mdoel to different combinations of factors, or to create lookup tables.

This is straightforward to do with `biosnicar` but it requires creating a new script for calling the `biosnicar` functions. The main concept to understand is that `setup_snicar()` is called once to instantiate all the necessary classes, then their associated values can be updated in each iteration of the code and used for the next simulation. 

There is one gotcha that users must be aware of when iterating over many `biosnicar` runs. This is the need to re-execute some class functions if certain fields in the `Ice` or `Illumination` instances are changed. Specifically, these classes have associated functions that calculate the refractive index from the ice optical properties and the irradiance from the solar zenith angle and illumination profile. This means that after updating values in any field in these classes, it is necessary to execute the `ice.calculate_refractive_index(input_file)` and/or `illumination.calculate_irradiance()` functions. This is not necessary for single runs because the functions are invoked when the class is first instantiated.

The code snippet below shows how to build a script for iterating over many input configurations. The runs are all run in serial, meaning there is no acceleration by spreading the runs across multiple processors. To see how to accelerate the code, skip to the section on `distributing biosnicar runs`.

```py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# save this file to the top level directory, then run from the command line
# as follows:
# python biosnicar_iterator.py

import numpy as np
from pathlib import Path

from biosnicar.adding_doubling_solver import adding_doubling_solver
from biosnicar.column_OPs import get_layer_OPs, mix_in_impurities
from biosnicar.display import display_out_data, plot_albedo
from biosnicar.setup_snicar import setup_snicar
from biosnicar.toon_rt_solver import toon_solver
from biosnicar.validate_inputs import validate_inputs

# run setup_snicar() to establish base-case values for ALL necessary params
(
    ice,
    illumination,
    rt_config,
    model_config,
    plot_config,
    impurities,
) = setup_snicar()

# now define the range of values you actually want to iterate over
lyrList = [0, 1]
densList = [400, 500, 600, 700, 800]
reffList = [200, 400, 600, 800, 1000]
zenList = [30, 40, 50, 60]
bcList = [500, 1000, 2000]
dzList = [
    [0.08, 0.1],
    [0.10, 0.15],
    [0.2, 0.5],
    [0.3, 0.5],
    [1, 10],
]

# set up an output array
ncols = (
    len(lyrList)
    * len(densList)
    * len(reffList)
    * len(zenList)
    * len(bcList)
    * len(dzList)
)

specOut = np.zeros(shape=(ncols, 481))

# iterate over all your values
counter = 0
for layer_type in lyrList:
    for density in densList:
        for reff in reffList:
            for zen in zenList:
                for bc in bcList:
                    for dz in dzList:
                        ice.dz = dz
                        ice.nbr_lyr = 2
                        ice.layer_type = [layer_type] * len(ice.dz)
                        ice.rho = [density] * len(ice.dz)
                        ice.rds = [reff] * len(ice.dz)
                        illumination.solzen = zen
                        # remember to recalculate irradiance values when any of the dependency values change
                        # i.e. irradiance is derived from solzen, so call the recalc func after updating solzen
                        illumination.calculate_irradiance()
                        impurities[0].conc = [
                            bc,
                            bc,
                        ]  # bc in all layers
                        # remember to recalculate RI after changing any ice optical values 
                        ice.calculate_refractive_index(input_file)

                        ssa_snw, g_snw, mac_snw = get_layer_OPs(ice, model_config)
                        tau, ssa, g, L_snw = mix_in_impurities(
                            ssa_snw,
                            g_snw,
                            mac_snw,
                            ice,
                            impurities,
                            model_config,
                        )

                        # now call the solver of your choice (here AD solver)
                        outputs = adding_doubling_solver(
                            tau, ssa, g, L_snw, ice, illumination, model_config
                        )

                        # spectral albedo appended to output array
                        specOut[counter, 0:480] = outputs.albedo
                        specOut[counter, 480] = outputs.BBA
                        counter += 1

# save to file
np.savetxt("biosnicar_multiple_runs.csv", specOut, delimiter=",")
```


## Distributing biosnicar runs

Iterating over many `biosnicar` runs is a very parallelizable process. This means the total number of runs can be split across many processor cores so that they can be executed simultaneously, rather than sequentially, one after the other. The more cores you have available, the faster the copde will execute. The code below is an example driver script that runs `biosnicar` with a large number of configurations, run in a distributed way across all the available cores. This is achieved using the `dask` package.

Note that both `dask` and `dask.distributed` are required dependencies. Ensure you have installed `dask` using `pip install dask[complete]` which includes all the necessary packages. 

If you are a linux user you can check your `dask` distributed `biosnicar` runs are working as expected using a command lione tool like `htop`. This tool allows you to see the usage of each available processing core on your machine. Depending how many cores you have, you should see `biosnicar` accouting for some percentage of the CPU usage on every available core.

```py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from pathlib import Path
import dask

from adding_doubling_solver import adding_doubling_solver
from column_OPs import get_layer_OPs, mix_in_impurities
from display import display_out_data, plot_albedo
from setup_snicar import setup_snicar
from toon_rt_solver import toon_solver
from validate_inputs import validate_inputs
from dask.distributed import Client

if __name__ == "__main__":
    client = Client()

    BIOSNICAR_SRC_PATH = Path(__file__).resolve().parent

    # define input file
    input_file = BIOSNICAR_SRC_PATH.joinpath("inputs.yaml").as_posix()
    print(input_file)

    lyrList = [0, 1]
    densList = [400, 500, 600, 700, 800]
    reffList = [200, 400, 600, 800, 1000]
    zenList = [30, 40, 50, 60]
    bcList = [500, 1000, 2000]
    dzList = [
        [0.08, 0.1],
        [0.10, 0.15],
        [0.2, 0.5],
        [0.3, 0.5],
        [1, 10],
    ]

    ncols = (
        len(lyrList)
        * len(densList)
        * len(reffList)
        * len(zenList)
        * len(bcList)
        * len(dzList)
    )

    @dask.delayed
    def run_using_dask(input_file, lyr, dens, reff, zen, bc, dz):
        (
            ice,
            illumination,
            rt_config,
            model_config,
            plot_config,
            impurities,
        ) = setup_snicar()

        ice.dz = dz
        ice.nbr_lyr = 2
        ice.layer_type = [lyr] * len(ice.dz)
        ice.rho = [dens] * len(ice.dz)
        ice.rds = [reff] * len(ice.dz)
        illumination.solzen = zen
        illumination.calculate_irradiance()
        impurities[0].conc = [
            bc,
            bc,
        ]  # bc in all layers
        ice.calculate_refractive_index(input_file)
        illumination.calculate_irradiance()

        ssa_snw, g_snw, mac_snw = get_layer_OPs(ice, model_config)
        tau, ssa, g, L_snw = mix_in_impurities(
            ssa_snw,
            g_snw,
            mac_snw,
            ice,
            impurities,
            model_config,
        )
        outputs = adding_doubling_solver(
            tau, ssa, g, L_snw, ice, illumination, model_config
        )

        return outputs.albedo

    Out = []
    # now use the reduced LUT to call snicar and obtain best matching spectrum
    for lyr in lyrList:
        for dens in densList:
            for reff in reffList:
                for zen in zenList:
                    for bc in bcList:
                        for dz in dzList:
                            out = run_using_dask(
                                input_file, lyr, dens, reff, zen, bc, dz
                            )
                            Out.append(out)

    result = dask.compute(*Out, scheduler="processes")
```
