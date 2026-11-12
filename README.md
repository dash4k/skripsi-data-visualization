# Skripsi Data Visualization

Python scripts for visualizing frame-rate benchmark data and image-quality metrics.

## What it does

- **FPS plots:** Visualizes frame timing for animation, frame-change, and process benchmarks, including average FPS and 1% low FPS.
- **FPS summary:** Compares average FPS and 1% low FPS across benchmark labels.
- **Quality plots:** Plots PSNR and SSIM per image, their distributions, and the relationship between the two metrics.

The scripts load the most recently modified CSV file matching the expected pattern in each data directory and save plots under the corresponding `outputs/` directory.

## Requirements

- Python 3.10 or later
- `pandas`
- `matplotlib`
- `numpy` (used by the quality plotting script)
- GNU Make, if using the Makefile

Install the Python dependencies:

```bash
python -m pip install pandas matplotlib numpy
```

## Data files

Place input CSV files in these directories:

| Directory | Expected files / columns |
|---|---|
| `fps/data/` | `frames_on_animation_changed_*.csv`, `frames_on_frame_changed_*.csv`, or `frames_on_process_*.csv`; each needs a `frame_ms` column |
| `fps/data/` | `benchmark_summary.csv`; needs `label`, `avg_fps`, and `1%_low_fps` columns |
| `quality/data/` | `results_*.csv`; needs `PSNR (dB)` and `SSIM` columns |

For FPS frame plots, the script selects the latest matching CSV for the selected benchmark type. The summary and quality scripts also select the most recently modified matching CSV.

## Run

From the repository root, run an individual plot with Python:

```bash
python -m fps.plot_frames animation
python -m fps.plot_frames frame
python -m fps.plot_frames process
python -m fps.plot_summary
python -m quality.plot
```

Or use the Makefile:

```bash
make fps-animation
make fps-frame
make fps-process
make fps-summary
make quality
```

Run all plots with:

```bash
make
```

The FPS plots are saved to `fps/outputs/`, and the quality plot is saved to `quality/outputs/`. The scripts also display each plot after generating it.