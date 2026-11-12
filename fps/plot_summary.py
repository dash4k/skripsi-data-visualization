import glob
import os
import pandas as pd
import matplotlib.pyplot as plt
from utils.path import FPS_SUMMARY, FPS_OUTPUTS


csv_files = glob.glob(str(FPS_SUMMARY))
if not csv_files:
    raise FileNotFoundError("No ./data/benchmark_summary.csv file found")
csv_path = max(csv_files, key=os.path.getmtime)
print(f"Loading {csv_path}")

df = pd.read_csv(csv_path)

g = df.groupby("label").agg(
    avg_fps=("avg_fps", "mean"),
    low_1pct=("1%_low_fps", "mean"),
).sort_values("avg_fps")

fig, ax = plt.subplots(figsize=(9, 5))

g[["avg_fps", "low_1pct"]].plot.barh(ax=ax)
ax.set_xlabel("FPS (higher is better)")
ax.set_ylabel("")
ax.set_title("Average vs 1% low FPS")

for container in ax.containers:
    ax.bar_label(container, fmt="%.1f", padding=3)

ax.set_xlim(0, g.max().max() * 1.12)

plt.tight_layout()
plt.savefig(f"{str(FPS_OUTPUTS)}/fps_benchmark_summary.png", dpi=300)
plt.show()