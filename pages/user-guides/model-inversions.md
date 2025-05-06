# Model inversions

The default way to run `biosnicar` is to provide input values and produce a spectral albedo. However, it is also possible to invert the model so that `biosnicar` predicts what input values lead to a given albedo. Perhaps you have some spectral albedo values measured using a spectroradiometer in the field. You have the time of day, measurement conditions and maybe a measurement for ice density. You could provide those measured values to `biosnicar` and use the model to fill in the gaps - providing `biosnicar`'s best guess for the ice-physical and impurity conditions that explain your spectrum. You can apply this logic to any missing input values.

There are several ways to achieve this. The 'right' way will depend on your specific use-case, but we can explore some options here.

## How it works

You run `biosnicar` with your known values fixed as constants (probably in `inputs.yaml`). Then, you iterate over a given range of values for the unknown parameters. You can then instruct `biosnicar` to stop once the predicted spectrum matches the 'reference' spectrum (e.g. one you measured in the field), or you can run over the whole parameter space and retrospectively look for the simulation that yielded the closest matching spectrum. The more values you iterate over, the more precise your prediction will be, at the cost of computation time.

## Running `biosnicar` 'on-the-fly'

If you only need to explore a small parameter space (maybe you have reliable field measuremeents for all but one or two parameters, or you can cope with a coarse resolution for your predictions), you could simply run `biosnicar` in a loop and either stop when some threshold accuracy is found or retrospectively identify the best-matching simulation after all the runs complete. The benefits of this are that it is simple to program, and if your parameter space is small (say hundreds to thousands of runs, not tens-to-hundreds-of-thousands of runs) then it does not require a lot of computational resources overall. You could adapt the example code provided on the [handling multiple runs](/handling-multiple-runs) page by loading a reference spectrum, and then in each iteration calculating your preferred type of error between the predicted and reference spectrum. You could either halt and report the model configuration when the calculated error was below a threshold, or you could append all the errors to an array and search for the smallest after the runs are complete.


## Using a lookup table

If you want to search a large parameter space, or you want to invert the model thousands of times across thousands of reference spectra, you might find it useful to use a lookup table approach. This is the way we favour for applying model inversions to remote sensing data, for example, where an inversion is done for each pixel in a multimillion-pixel image. In this case, you do the `biosnicar` runs once only, but over a large parameter space, generating a multidimensional array with dimensions for all the input values and the spectral albedo. Then, for each reference spectrum you can search the array to find the minimum error and recreate the model config from the indexes in each dimension. The advantages of this are that it is computationally efficient in your actual application because lookups from an array are much cheaper than running the `biosnicar` model. This is especially true if you can use a prebuilt lookup table. Example code can be found in the classic branch under `LUTgenerator.py`, and example code for the master branch will come soon.

## Emulating biosnicar

When the parameter space is simply too large to build look-up tables that can be produced in a reasonable amount of time and/or stored in a reasonable size, another option is to use an emulator with optimization algorithms. This section will be more developed soon, but you can find examples in Bohn et al. 2022 (Gaussian processes emulator) and Chevrollier et al. 2024 (Deep learning emulator). 
