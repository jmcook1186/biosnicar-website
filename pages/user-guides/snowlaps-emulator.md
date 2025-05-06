# Snowlaps: A Deep Learning Emulator for Biosnicar

`snowlaps` is a Python package that provides a fast, flexible alternative to the full biosnicar radiative transfer model. 
Built on a deep learning emulator trained on biosnicar v2.1 outputs, snowlaps enables rapid prediction and inversion of snow spectral albedo, making it a powerful tool for researchers and practitioners working with snow surface properties and light absorbing particles (LAPs). It is a lightweight and fast alternative to the full model for users that only need the core features of `biosnicar`.

## What is Snowlaps?

`snowlaps` was originally developed to study the impact of different LAPs on snow spectral albedo in Southern Norway. 
It has since evolved into a general-purpose library with two main use cases:

- **Forward mode**: Predict snow spectral albedo from prescribed surface properties, serving as a fast alternative to running the full biosnicar model.
- **Inverse mode**: Infer surface properties from observed snow spectral albedo, enabling efficient parameter estimation and data analysis.
  
## How Does Snowlaps Relate to Biosnicar?

The core of `snowlaps` is a deep learning emulator trained on a large set of biosnicar v2.1 simulations. 
This means that snowlaps can reproduce biosnicar’s outputs with high fidelity, but at a fraction of the computational cost. `snowlaps` is ideal for applications that require many model evaluations, such as sensitivity analyses, uncertainty quantification, or real-time data processing. It is likely to be more attractive than the ful model for many users, but power users that need to use the advanced features and/or full parameter space offered by `biosnicar` or want to build features on top of the core `biosnicar` functions should use the full model.

## Why Use Snowlaps?

- Speed: The deep learning emulator provides near-instantaneous predictions, compared to the much longer runtimes of the full biosnicar model.
- Convenience: snowlaps can be used as a Python package or via an interactive Streamlit app, making it accessible for both scripting and exploratory analysis.
- Versatility: Supports both forward and inverse modeling, allowing users to predict albedo from surface properties or infer properties from measurements.
- Reproducibility: Trained directly on biosnicar outputs, ensuring consistency with the original model.

## Usage
### Installation

You can install snowlaps using conda and pip:

1) clone repository in the folder of your choice
   
`git clone git@github.com:openosmia/snowlaps.git`

2) move into snowlaps directory

`cd snowlaps`

3) create conda environment
   
`conda env create -f environment.yml`

4) activate conda environment

`conda activate snowlaps`

5) install snowlaps

`pip install -e .`


### Run

`snowlaps` can be used in two main ways:
- As a Python package: Integrate snowlaps into your own scripts and workflows.
- Via the Streamlit app: Run an interactive web app for quick experimentation and visualization.

Example scripts are provided in the snowlaps/examples directory, including:

- Forward runs of the snowlaps emulator
- Inversion of hyperspectral albedo measurements
- Comparison of snowlaps and biosnicar predictions


## Citation

If you use snowlaps in your research, please cite:

Chevrollier, L.-A., Wehrlé, A., Cook, J. M., Pirk, N., Benning, L. G., Anesio, A. M., and Tranter, M.: Separating the albedo reducing effect of different light absorbing particles on snow using deep learning, EGUsphere [preprint], https://doi.org/10.5194/egusphere-2024-2583, 2024.
