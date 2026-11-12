import glob
import os
import re
import sys
import pandas as pd
import matplotlib.pyplot as plt
from utils.path import FPS_ANIMATION, FPS_FRAME, FPS_PROCESS, FPS_OUTPUTS

file = sys.argv[1]
match file:
    case "animation":
        path = FPS_ANIMATION
    case "frame":
        path = FPS_FRAME
    case "process":
            path = FPS_PROCESS
    case _:
          raise SystemError("Invalid file")

path = str(path)
output_path = re.search(r"frames.*(?=_)", path)
csv_files = glob.glob(path)
if not csv_files:
    raise FileNotFoundError(f"No {path} file found")
csv_path = max(csv_files, key=os.path.getmtime)
print(f"Loading {csv_path}")

window_s = 0.5

df = pd.read_csv(csv_path)
ms = df["frame_ms"]

t = ms.cumsum() / 1000.0

avg_fps = 1000.0 / ms.mean()
low_1pct = 1000.0 / ms.quantile(0.99)

inst_fps = 1000.0 / ms

bins = (t // window_s).astype(int)
grouped = df.assign(bin=bins).groupby("bin")["frame_ms"]
win_fps = grouped.count() / (grouped.sum() / 1000.0)
win_t = (win_fps.index + 0.5) * window_s

fig, ax = plt.subplots(figsize=(14, 5))

ax.plot(t, inst_fps, linewidth=0.4, alpha=0.25, color="tab:blue", label="per-frame FPS")
ax.plot(win_t, win_fps.values, linewidth=1.5, color="tab:orange",
        label=f"FPS ({window_s}s windows)")
ax.axhline(avg_fps, color="green", linestyle="--", label=f"avg {avg_fps:.1f}")
ax.axhline(low_1pct, color="red", linestyle="--", label=f"1% low {low_1pct:.1f}")
ax.axhline(60, color="gray", linestyle=":", label="60 FPS")

ax.set_xlabel("Time (s)")
ax.set_ylabel("FPS (higher is better)")
ax.set_title(f"{output_path.group()}\navg {avg_fps:.1f} FPS | 1% low {low_1pct:.1f} FPS")
ax.set_ylim(0, min(inst_fps.max(), avg_fps * 2))
ax.legend(loc="lower right")

fig.tight_layout()

plt.savefig(f"{str(FPS_OUTPUTS)}/{output_path.group()}.png", dpi=300)
plt.show()