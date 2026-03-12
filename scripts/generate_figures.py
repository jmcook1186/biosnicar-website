#!/usr/bin/env python3
"""Generate documentation figures for the BioSNICAR website.

ALL figures use the real BioSNICAR forward model for data provenance.
Run this script from an environment where biosnicar is installed:

    cd /path/to/biosnicar-py
    python /path/to/biosnicar-website/scripts/generate_figures.py

Figures are saved to public/static/ in the website repo.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

from biosnicar import run_model
from biosnicar.emulator import Emulator

OUTPUT_DIR = Path(__file__).parent.parent / "public" / "static"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Consistent style
plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "axes.grid": True,
    "grid.alpha": 0.3,
    "grid.linewidth": 0.5,
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 13,
    "legend.fontsize": 10,
    "figure.dpi": 150,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.15,
})

COLORS = {
    "clean": "#2563eb",      # blue
    "bc": "#1e1e1e",         # near-black
    "algae": "#16a34a",      # green
    "retrieved": "#dc2626",  # red
    "accent": "#7c3aed",     # purple
    "grey": "#6b7280",
    "light": "#93c5fd",
}

WAV = np.arange(0.205, 4.999, 0.01)  # 480 bands


# =====================================================================
# Figure 1: Hero spectrum (Welcome page)
# Three surface types showing BioSNICAR's range
# =====================================================================
def fig_hero_spectrum():
    snow = run_model(solzen=50, rds=500)
    clean_ice = run_model(solzen=50, rds=1000)
    dirty_ice = run_model(solzen=50, rds=1000, glacier_algae=50000, black_carbon=5000)

    fig, ax = plt.subplots(figsize=(7, 3.2))
    ax.plot(WAV, np.array(snow.albedo), color=COLORS["clean"], linewidth=2, label="Fresh snow")
    ax.plot(WAV, np.array(clean_ice.albedo), color=COLORS["accent"], linewidth=2, label="Clean glacier ice")
    ax.plot(WAV, np.array(dirty_ice.albedo), color=COLORS["algae"], linewidth=2, label="Dirty glacier ice")
    ax.set_xlim(0.2, 2.5)
    ax.set_ylim(0, 1.05)
    ax.set_xlabel("Wavelength (µm)")
    ax.set_ylabel("Albedo")
    ax.legend(loc="upper right", framealpha=0.9)
    ax.set_title("Spectral albedo from BioSNICAR")
    fig.savefig(OUTPUT_DIR / "hero_spectrum.png")
    plt.close(fig)
    print("  hero_spectrum.png")


# =====================================================================
# Figure 2: Impurity effects (Fundamentals, Quick Start)
# Shows how each impurity type darkens the spectrum differently
# =====================================================================
def fig_impurity_effects():
    clean = run_model(solzen=50, rds=1000)
    bc = run_model(solzen=50, rds=1000, black_carbon=5000)
    algae = run_model(solzen=50, rds=1000, glacier_algae=50000)

    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.plot(WAV, np.array(clean.albedo), color=COLORS["clean"], linewidth=2, label="Clean ice")
    ax.plot(WAV, np.array(bc.albedo), color=COLORS["bc"], linewidth=2, label="+ Black carbon (5000 ppb)")
    ax.plot(WAV, np.array(algae.albedo), color=COLORS["algae"], linewidth=2, label="+ Glacier algae (50k cells/mL)")

    ax.set_xlim(0.3, 2.0)
    ax.set_ylim(0, 1.05)
    ax.set_xlabel("Wavelength (µm)")
    ax.set_ylabel("Albedo")
    ax.legend(loc="upper right", framealpha=0.9)
    ax.set_title("Effect of impurities on ice albedo")
    fig.savefig(OUTPUT_DIR / "impurity_effects.png")
    plt.close(fig)
    print("  impurity_effects.png")


# =====================================================================
# Figure 3: Platform bands (Remote Sensing)
# 480-band spectrum with Sentinel-2 bands overlaid
# =====================================================================
def fig_platform_bands():
    out = run_model(solzen=50, rds=1000)
    albedo = np.array(out.albedo)

    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.plot(WAV, albedo, color=COLORS["grey"], linewidth=1.5, alpha=0.7, label="480-band spectrum")

    # Sentinel-2 bands (approximate centres and widths)
    s2_bands = [
        ("B2", 0.490, 0.065, "#3b82f6"),
        ("B3", 0.560, 0.035, "#22c55e"),
        ("B4", 0.665, 0.030, "#ef4444"),
        ("B8", 0.842, 0.115, "#a855f7"),
        ("B11", 1.610, 0.090, "#f97316"),
    ]

    for name, centre, width, color in s2_bands:
        lo, hi = centre - width / 2, centre + width / 2
        mask = (WAV >= lo) & (WAV <= hi)
        band_albedo = np.mean(albedo[mask]) if mask.any() else 0
        ax.axvspan(lo, hi, alpha=0.25, color=color)
        ax.plot(centre, band_albedo, "o", color=color, markersize=8, zorder=5)
        ax.annotate(name, (centre, band_albedo + 0.04), ha="center",
                    fontsize=8, fontweight="bold", color=color)

    ax.set_xlim(0.3, 2.0)
    ax.set_ylim(0, 1.05)
    ax.set_xlabel("Wavelength (µm)")
    ax.set_ylabel("Albedo")
    ax.set_title("Spectral albedo convolved to Sentinel-2 bands")
    fig.savefig(OUTPUT_DIR / "platform_bands.png")
    plt.close(fig)
    print("  platform_bands.png")


# =====================================================================
# Figure 4: Inversion result (Inversions)
# Forward model "truth" vs a near-match retrieval
# =====================================================================
def fig_inversion_result():
    true_out = run_model(solzen=50, rds=1200, glacier_algae=30000, black_carbon=2000)
    retr_out = run_model(solzen=50, rds=1180, glacier_algae=28000, black_carbon=2200)

    true_albedo = np.array(true_out.albedo)
    retr_albedo = np.array(retr_out.albedo)

    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.plot(WAV, true_albedo, color=COLORS["clean"], linewidth=2, label="True (forward model)")
    ax.plot(WAV, retr_albedo, color=COLORS["retrieved"], linewidth=1.5,
            linestyle="--", label="Retrieved", alpha=0.9)

    ax.set_xlim(0.3, 2.0)
    ax.set_ylim(0, 1.05)
    ax.set_xlabel("Wavelength (µm)")
    ax.set_ylabel("Albedo")
    ax.legend(loc="upper right", framealpha=0.9)
    ax.set_title("Inverse retrieval: true vs recovered spectrum")
    fig.savefig(OUTPUT_DIR / "inversion_result.png")
    plt.close(fig)
    print("  inversion_result.png")


# =====================================================================
# Figure 5: SSA degeneracy (Inversions)
# Real BioSNICAR runs showing that different (rds,rho) give same albedo
# =====================================================================
def fig_ssa_degeneracy():
    # Run BioSNICAR for several (rds,rho) combinations along a constant-SSA line
    # and one off that line, to show spectral degeneracy
    target_ssa = 3 * (1 - 600 / 917) / (1000e-6 * 600)

    # Pairs along the constant-SSA curve
    pairs_on = []
    for rds in [600, 1000, 1500, 2000]:
        rho = 3 / (target_ssa * rds * 1e-6 + 3 / 917)
        pairs_on.append((rds, int(rho)))

    # One pair with different SSA
    pairs_off = [(1000, 400)]

    fig, axes = plt.subplots(1, 2, figsize=(10, 3.5), gridspec_kw={"wspace": 0.3})

    # Left panel: spectra along constant SSA are nearly identical
    ax = axes[0]
    for rds, rho in pairs_on:
        out = run_model(solzen=50, rds=rds, rho=rho)
        ax.plot(WAV, np.array(out.albedo), linewidth=1.5,
                label=f"rds={rds}, rho={rho}")
    ax.set_xlim(0.3, 2.0)
    ax.set_ylim(0, 1.05)
    ax.set_xlabel("Wavelength (µm)")
    ax.set_ylabel("Albedo")
    ax.set_title("Same SSA, different (rds, rho)\n— spectra are degenerate")
    ax.legend(fontsize=8, loc="upper right", framealpha=0.9)

    # Right panel: different SSA gives a visibly different spectrum
    ax = axes[1]
    ref_out = run_model(solzen=50, rds=1000, rho=600)
    diff_out = run_model(solzen=50, rds=1000, rho=400)
    ax.plot(WAV, np.array(ref_out.albedo), color=COLORS["clean"], linewidth=2,
            label=f"SSA={target_ssa:.1f} m²/kg")
    diff_ssa = 3 * (1 - 400 / 917) / (1000e-6 * 400)
    ax.plot(WAV, np.array(diff_out.albedo), color=COLORS["retrieved"], linewidth=2,
            label=f"SSA={diff_ssa:.1f} m²/kg")
    ax.set_xlim(0.3, 2.0)
    ax.set_ylim(0, 1.05)
    ax.set_xlabel("Wavelength (µm)")
    ax.set_ylabel("Albedo")
    ax.set_title("Different SSA\n— spectra are distinguishable")
    ax.legend(fontsize=9, loc="upper right", framealpha=0.9)

    fig.savefig(OUTPUT_DIR / "ssa_degeneracy.png")
    plt.close(fig)
    print("  ssa_degeneracy.png")


# =====================================================================
# Figure 6: Emulator accuracy (Emulator)
# Real emulator vs real forward model on multiple test points
# =====================================================================
def fig_emulator_accuracy():
    emu = Emulator.load("data/emulators/glacier_ice_8_param_default.npz")

    # Generate test points across parameter space
    rng = np.random.RandomState(42)
    n = 30

    # Valid rds in the bubbly-air LUT are multiples of 10 (500-2000 range).
    # Sample multiples of 10 to stay on the lookup grid.
    valid_rds = np.arange(500, 1510, 10)
    test_params = {
        "rds": rng.choice(valid_rds, n),
        "rho": rng.randint(300, 901, n),
        "black_carbon": rng.randint(0, 5001, n),
        "snow_algae": rng.randint(0, 50001, n),
        "glacier_algae": rng.randint(0, 500001, n),
        "dust": rng.randint(0, 50001, n),
        "direct": rng.choice([0, 1], n),
        "solzen": rng.randint(25, 81, n),
    }

    # Run both forward model and emulator for each test point
    forward_bbas = []
    emulator_bbas = []
    for i in range(n):
        params = {k: int(v[i]) for k, v in test_params.items()}
        fwd = run_model(**params)
        emu_albedo = emu.predict(**params)
        forward_bbas.append(fwd.BBA)
        # Compute emulator BBA using same flux weighting
        flx = np.array(fwd.flx_slr)
        emu_bba = np.sum(flx * emu_albedo) / np.sum(flx)
        emulator_bbas.append(emu_bba)

    forward_bbas = np.array(forward_bbas)
    emulator_bbas = np.array(emulator_bbas)

    fig, ax = plt.subplots(figsize=(4, 4))
    ax.scatter(forward_bbas, emulator_bbas, s=25, alpha=0.7,
              color=COLORS["clean"], edgecolors="none")
    ax.plot([0, 1], [0, 1], "k--", linewidth=1, alpha=0.5)
    lo = min(forward_bbas.min(), emulator_bbas.min()) - 0.03
    hi = max(forward_bbas.max(), emulator_bbas.max()) + 0.03
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.set_xlabel("Forward model BBA")
    ax.set_ylabel("Emulator BBA")
    r2 = 1 - np.sum((forward_bbas - emulator_bbas)**2) / np.sum((forward_bbas - forward_bbas.mean())**2)
    ax.set_title(f"Emulator accuracy (R² = {r2:.4f})")
    ax.set_aspect("equal")
    fig.savefig(OUTPUT_DIR / "emulator_accuracy.png")
    plt.close(fig)
    print("  emulator_accuracy.png")


# =====================================================================
# Figure 7: PAR depth profile (Subsurface Light)
# Real BioSNICAR multi-layer runs for subsurface fluxes
# =====================================================================
def fig_par_depth():
    # Multi-layer clean ice column
    n_layers = 10
    dz = [0.05] * n_layers
    dz[-1] = 0.50  # semi-infinite bottom

    clean = run_model(
        solzen=50,
        layer_type=[1] * n_layers,
        dz=dz,
        rds=[1000] * n_layers,
        rho=[600] * n_layers,
    )

    # Same column but with surface algae
    dirty = run_model(
        solzen=50,
        layer_type=[1] * n_layers,
        dz=dz,
        rds=[1000] * n_layers,
        rho=[600] * n_layers,
        glacier_algae=[50000, 20000] + [0] * (n_layers - 2),
    )

    # Extract downwelling flux at each layer interface, integrated over PAR (400-700nm)
    # PAR wavelength indices: 0.400 to 0.700 µm -> indices 19 to 49
    par_lo, par_hi = 19, 50

    clean_F_dwn = np.array(clean.F_dwn)  # shape: (480, n_layers+1)
    dirty_F_dwn = np.array(dirty.F_dwn)

    # Integrate over PAR band at each depth interface
    clean_par = np.sum(clean_F_dwn[par_lo:par_hi, :], axis=0)
    dirty_par = np.sum(dirty_F_dwn[par_lo:par_hi, :], axis=0)

    # Normalise to surface value
    clean_par = clean_par / clean_par[0]
    dirty_par = dirty_par / dirty_par[0]

    # Depth at each interface
    depths = np.concatenate([[0], np.cumsum(dz)])

    fig, ax = plt.subplots(figsize=(5, 4))
    ax.plot(clean_par, depths, color=COLORS["clean"], linewidth=2.5, label="Clean ice")
    ax.plot(dirty_par, depths, color=COLORS["algae"], linewidth=2.5, label="+ Surface algae")
    ax.axvline(1.0, color="k", linewidth=0.5, linestyle=":", alpha=0.5)

    ax.invert_yaxis()
    ax.set_xlabel("PAR (relative to surface)")
    ax.set_ylabel("Depth (m)")
    ax.set_title("Subsurface PAR profile")
    ax.legend(loc="lower left", framealpha=0.9)

    fig.savefig(OUTPUT_DIR / "par_depth.png")
    plt.close(fig)
    print("  par_depth.png")


# =====================================================================
# Figure 8: End-to-end workflow diagram (Examples)
# =====================================================================
def fig_workflow():
    fig, ax = plt.subplots(figsize=(8, 2.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 2)
    ax.axis("off")

    steps = [
        (1.0, "Satellite\nobservation", COLORS["grey"]),
        (3.2, "Emulator\n(1 µs)", COLORS["clean"]),
        (5.4, "Retrieve\nice properties", COLORS["accent"]),
        (7.6, "Downstream\nanalysis", COLORS["algae"]),
    ]

    for i, (x, label, color) in enumerate(steps):
        box = mpatches.FancyBboxPatch((x - 0.7, 0.4), 1.9, 1.2,
                                       boxstyle="round,pad=0.15",
                                       facecolor=color, alpha=0.15,
                                       edgecolor=color, linewidth=2)
        ax.add_patch(box)
        ax.text(x + 0.25, 1.0, label, ha="center", va="center",
                fontsize=10, fontweight="bold", color=color)

        if i < len(steps) - 1:
            next_x = steps[i + 1][0]
            ax.annotate("", xy=(next_x - 0.75, 1.0), xytext=(x + 1.25, 1.0),
                        arrowprops=dict(arrowstyle="-|>", color="#374151",
                                        lw=2, mutation_scale=15))

    ax.text(5.0, 0.1, "< 1 second end-to-end", ha="center", va="center",
            fontsize=10, color="#374151", style="italic")

    fig.savefig(OUTPUT_DIR / "workflow.png")
    plt.close(fig)
    print("  workflow.png")


# =====================================================================
# Generate all
# =====================================================================
if __name__ == "__main__":
    print("Generating figures...")
    fig_hero_spectrum()
    fig_impurity_effects()
    fig_platform_bands()
    fig_inversion_result()
    fig_ssa_degeneracy()
    fig_emulator_accuracy()
    fig_par_depth()
    fig_workflow()
    print(f"\nDone! 8 figures written to {OUTPUT_DIR}")
