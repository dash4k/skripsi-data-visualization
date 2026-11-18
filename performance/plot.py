import os
import glob
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from utils.path import PERFORMANCE, PERFORMANCE_OUTPUTS


csv_files = glob.glob(str(PERFORMANCE))
if not csv_files:
    raise FileNotFoundError("No results_*.csv file found")
csv_path = max(csv_files, key=os.path.getmtime)
print(f"Loading {csv_path}")

df = pd.read_csv(csv_path)
tp, fp, tn, fn = df.loc[0, ["tp", "fp", "tn", "fn"]]

cm = np.array([[tn, fp],
               [fn, tp]])

labels = np.array([[f"{v}\n({v/cm.sum():.0%})" for v in row] for row in cm])

plt.figure(figsize=(5, 4))
sns.heatmap(cm, annot=labels, fmt="", cmap="Blues", cbar=True,
            xticklabels=["Verified Neg", "Verified Pos"],
            yticklabels=["Actual Neg", "Actual Pos"])
plt.title("Confusion Matrix")
plt.ylabel("Actual")
plt.xlabel("Verified")
plt.tight_layout()
plt.savefig(f"{str(PERFORMANCE_OUTPUTS)}/confusion_matrix.png", dpi=300)
plt.show()
