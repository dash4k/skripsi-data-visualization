import glob
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from utils.path import QUALITY, QUALITY_OUTPUTS

csv_files = glob.glob(str(QUALITY))
if not csv_files:
    raise FileNotFoundError("No results_*.csv file found")
csv_path = max(csv_files, key=os.path.getmtime)
print(f"Loading {csv_path}")

df = pd.read_csv(csv_path)
df["PSNR (dB)"] = df["PSNR (dB)"].replace(np.inf, np.nan)

fig, axes = plt.subplots(2, 2, figsize=(14, 7))

axes[0, 0].plot(df.index, df["PSNR (dB)"], marker="o", color="tab:blue")
axes[0, 0].axhline(df["PSNR (dB)"].mean(), color="red", linestyle="--",
                   label=f"Mean = {df['PSNR (dB)'].mean():.2f} dB")
axes[0, 0].set_title("PSNR per Image")
axes[0, 0].set_xlabel("Image index")
axes[0, 0].set_ylabel("PSNR (dB)")
axes[0, 0].legend()
axes[0, 0].grid(alpha=0.3)

axes[0, 1].plot(df.index, df["SSIM"], marker="s", color="tab:green")
axes[0, 1].axhline(df["SSIM"].mean(), color="red", linestyle="--",
                   label=f"Mean = {df['SSIM'].mean():.4f}")
axes[0, 1].set_title("SSIM per Image")
axes[0, 1].set_xlabel("Image index")
axes[0, 1].set_ylabel("SSIM")
axes[0, 1].legend()
axes[0, 1].grid(alpha=0.3)

axes[1, 0].hist(df["PSNR (dB)"].dropna(), bins=20, color="tab:blue", edgecolor="black")
axes[1, 0].set_title("PSNR Distribution")
axes[1, 0].set_xlabel("PSNR (dB)")
axes[1, 0].set_ylabel("Count")

axes[1, 1].scatter(df["PSNR (dB)"], df["SSIM"], alpha=0.7, color="tab:purple")
axes[1, 1].set_title("PSNR vs SSIM")
axes[1, 1].set_xlabel("PSNR (dB)")
axes[1, 1].set_ylabel("SSIM")
axes[1, 1].grid(alpha=0.3)

plt.tight_layout()
plt.savefig(f"{str(QUALITY_OUTPUTS)}/metrics_plot.png", dpi=300)
plt.show()