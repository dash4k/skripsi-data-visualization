# Skripsi Data Visualization

An interactive data-visualization project for analyzing frame-rate benchmarks, image-quality metrics, and detection accuracy.

The repository includes a Streamlit dashboard plus standalone Matplotlib and Seaborn plotting scripts.

## Features

### Interactive dashboard

`dashboard.py` provides a Streamlit dashboard with three tabs:

- **Performance**: FPS comparisons, run exploration, average FPS, 1% low FPS, and run consistency
- **Quality**: PSNR and SSIM charts, distributions, and raw image-quality data
- **Accuracy**: confusion matrix, accuracy, precision, recall, and F1 score

### Command-line plots

Standalone scripts generate static PNG files:

- FPS plots for no-tamper-detection, animation, frame, and process benchmarks
- FPS benchmark summary
- PSNR and SSIM quality plots
- Detection confusion matrix

## Requirements

- Python 3.10 or later
- `pip`
- GNU Make, if using the Makefile commands
- A graphical environment for standalone Matplotlib plots

Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

The project uses Streamlit, Plotly, Pandas, NumPy, Matplotlib, Seaborn, Pillow, and Altair.

## Running the Dashboard

From the repository root:

```bash
streamlit run dashboard.py
```

Streamlit will print a local URL, normally:

```text
http://localhost:8501
```

The dashboard automatically reads the latest matching CSV file in each data directory.

## Running the Static Plots

Run an individual FPS plot:

```bash
python -m fps.plot_frames no_tamper_detection
python -m fps.plot_frames animation
python -m fps.plot_frames frame
python -m fps.plot_frames process
```

Generate the FPS summary:

```bash
python -m fps.plot_summary
```

Generate the quality plots:

```bash
python -m quality.plot
```

Generate the confusion matrix:

```bash
python -m performance.plot
```

Alternatively, use the Makefile:

```bash
make fps-no-tamper-detection
make fps-animation
make fps-frame
make fps-process
make fps-summary
make quality
make performance
make dashboard
```

Generate the FPS summary and quality plots together:

```bash
make
```

## Data Structure

```text
fps/
├── data/
│   ├── benchmark_summary.csv
│   ├── frames_no_tamper_detection_*.csv
│   ├── frames_on_animation_changed_*.csv
│   ├── frames_on_frame_changed_*.csv
│   └── frames_on_process_*.csv
└── outputs/

quality/
├── data/
│   └── results_*.csv
└── outputs/

performance/
├── data/
│   └── results_*.csv
└── outputs/

utils/
└── path.py
```

## CSV Formats

### FPS frame data

Files matched by:

```text
fps/data/frames_no_tamper_detection_*.csv
fps/data/frames_on_animation_changed_*.csv
fps/data/frames_on_frame_changed_*.csv
fps/data/frames_on_process_*.csv
```

Each file must contain a `frame_ms` column containing frame rendering time in milliseconds.

### FPS summary data

`fps/data/benchmark_summary.csv` must contain:

| Column | Description |
|---|---|
| `label` | Benchmark configuration name |
| `avg_fps` | Average frames per second |
| `1%_low_fps` | 1% low FPS value |

### Image-quality data

Files in `quality/data/results_*.csv` must contain:

| Column | Description |
|---|---|
| `PSNR (dB)` | Peak Signal-to-Noise Ratio in decibels |
| `SSIM` | Structural Similarity Index |

Infinity-valued PSNR values, representing identical images, are handled as missing values in the charts and averages.

### Detection performance data

Files in `performance/data/results_*.csv` must contain one row with:

| Column | Description |
|---|---|
| `tp` | True positives |
| `fp` | False positives |
| `tn` | True negatives |
| `fn` | False negatives |

## Generated Outputs

| Script | Output |
|---|---|
| `fps/plot_frames.py` | `fps/outputs/<benchmark>.png` |
| `fps/plot_summary.py` | `fps/outputs/fps_benchmark_summary.png` |
| `quality/plot.py` | `quality/outputs/metrics_plot.png` |
| `performance/plot.py` | `performance/outputs/confusion_matrix.png` |

Remove generated PNG files with:

```bash
make clean
```

## Project Structure

```text
.
├── dashboard.py             # Interactive Streamlit dashboard
├── fps/
│   ├── data/                # FPS benchmark CSV data
│   ├── outputs/             # Generated FPS charts
│   ├── plot_frames.py       # Individual FPS run plot
│   └── plot_summary.py      # FPS benchmark comparison
├── quality/
│   ├── data/                # PSNR and SSIM CSV data
│   ├── outputs/             # Generated quality charts
│   └── plot.py
├── performance/
│   ├── data/                # Confusion-matrix CSV data
│   ├── outputs/             # Generated performance charts
│   └── plot.py
├── utils/
│   └── path.py              # Shared repository-relative paths
├── Makefile
└── requirements.txt
```