# dashboard.py
import glob
import os
import re

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.path import (
    FPS_NO_TAMPER_DETECTION, FPS_ANIMATION, FPS_FRAME, FPS_PROCESS,
    FPS_SUMMARY, QUALITY, PERFORMANCE,
)

st.set_page_config(page_title="Benchmark Dashboard", layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 2rem; max-width: 1400px;}
[data-testid="stMetric"] {
    background: rgba(128,128,128,.07);
    border: 1px solid rgba(128,128,128,.25);
    padding: 12px 16px;
    border-radius: 10px;
}
[data-testid="stMetricLabel"] {opacity: .75;}
.stTabs [data-baseweb="tab"] {font-size: 1.05rem; padding: 8px 18px;}
</style>
""", unsafe_allow_html=True)

PLOT_CFG = {"displaylogo": False, "modeBarButtonsToRemove": ["lasso2d", "select2d"]}
GRID = "rgba(128,128,128,.18)"


# ---------------------------------------------------------------- helpers
def latest_csv(pattern) -> str:
    files = glob.glob(str(pattern))
    if not files:
        raise FileNotFoundError(f"No file found for {pattern}")
    return max(files, key=os.path.getmtime)


@st.cache_data(show_spinner=False)
def load_csv(path: str, mtime: float) -> pd.DataFrame:
    return pd.read_csv(path)


def read_latest(pattern):
    path = latest_csv(pattern)
    return path, load_csv(path, os.path.getmtime(path))


def pct(x) -> str:
    return "n/a" if x != x else f"{x:.2%}"


def style(fig, x=None, y=None, height=380, legend_right=False):
    """Shared look for every chart."""
    legend = (dict(orientation="v", x=1.01, y=1) if legend_right else
              dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    fig.update_layout(
        height=height, xaxis_title=x, yaxis_title=y, legend=legend,
        margin=dict(l=10, r=10, t=40, b=10), hoverlabel=dict(font_size=13),
    )
    fig.update_xaxes(showgrid=True, gridcolor=GRID, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor=GRID, zeroline=False)
    return fig


# ---------------------------------------------------------------- FPS plots
FPS_SOURCES = {
    "No tamper detection": FPS_NO_TAMPER_DETECTION,
    "Animation": FPS_ANIMATION,
    "Frame": FPS_FRAME,
    "Process": FPS_PROCESS,
}


def natural_key(s: str):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]


def list_csvs(pattern) -> list[str]:
    files = glob.glob(str(pattern))
    if not files:
        raise FileNotFoundError(f"No files found for {pattern}")
    return sorted(files, key=lambda f: natural_key(os.path.basename(f)))


def fps_stats(df: pd.DataFrame, window_s: float):
    ms = df["frame_ms"]
    t = ms.cumsum() / 1000.0
    inst_fps = 1000.0 / ms
    avg_fps = 1000.0 / ms.mean()
    low_1pct = 1000.0 / ms.quantile(0.99)

    bins = (t // window_s).astype(int)
    grouped = df.assign(bin=bins).groupby("bin")["frame_ms"]
    win_fps = grouped.count() / (grouped.sum() / 1000.0)
    win_t = (win_fps.index + 0.5) * window_s
    return t, inst_fps, win_t, win_fps, avg_fps, low_1pct


def fps_all_runs_fig(files: list[str], window_s: float):
    fig = go.Figure()
    series, rows = [], []

    for f in files:
        df = load_csv(f, os.path.getmtime(f))
        _, _, win_t, win_fps, avg, low = fps_stats(df, window_s)
        name = os.path.splitext(os.path.basename(f))[0]
        fig.add_trace(go.Scatter(
            x=win_t, y=win_fps.values, mode="lines", name=name,
            line=dict(width=1.2), opacity=0.7,
            hovertemplate=f"{name}<br>%{{x:.1f}}s: %{{y:.1f}} FPS<extra></extra>",
        ))
        series.append(win_fps.rename(name))
        rows.append({"run": name, "avg_fps": avg, "1%_low_fps": low})

    stacked = pd.concat(series, axis=1)
    mean_fps = stacked.mean(axis=1)[stacked.count(axis=1) >= 2]
    fig.add_trace(go.Scatter(
        x=(mean_fps.index + 0.5) * window_s, y=mean_fps.values, mode="lines",
        name="mean of all runs", line=dict(color="#e11d48", width=3.5),
        hovertemplate="mean<br>%{x:.1f}s: %{y:.1f} FPS<extra></extra>",
    ))

    summary = pd.DataFrame(rows).set_index("run")
    fig.add_hline(y=60, line_dash="dot", line_color="gray",
                  annotation_text="60 FPS", annotation_position="top left")
    fig.update_yaxes(rangemode="tozero")
    return style(fig, "Time (s)", "FPS", height=480, legend_right=True), summary


def fps_single_run_fig(df: pd.DataFrame, window_s: float):
    t, inst_fps, win_t, win_fps, avg_fps, low_1pct = fps_stats(df, window_s)

    fig = go.Figure()
    fig.add_trace(go.Scattergl(
        x=t, y=inst_fps, mode="lines", name="per-frame FPS",
        line=dict(width=1, color="#3b82f6"), opacity=0.3,
    ))
    fig.add_trace(go.Scatter(
        x=win_t, y=win_fps.values, mode="lines", name=f"{window_s}s window",
        line=dict(width=2.5, color="#f97316"),
    ))
    fig.add_hline(y=avg_fps, line_dash="dash", line_color="#16a34a",
                  annotation_text=f"avg {avg_fps:.1f}", annotation_position="top left")
    fig.add_hline(y=low_1pct, line_dash="dash", line_color="#dc2626",
                  annotation_text=f"1% low {low_1pct:.1f}", annotation_position="bottom left")
    fig.add_hline(y=60, line_dash="dot", line_color="gray",
                  annotation_text="60 FPS", annotation_position="top left")
    fig.update_yaxes(range=[0, min(inst_fps.max(), avg_fps * 2)])
    return style(fig, "Time (s)", "FPS", height=450), avg_fps, low_1pct


def fps_summary_fig(df: pd.DataFrame):
    g = df.groupby("label").agg(
        avg_fps=("avg_fps", "mean"),
        low_1pct=("1%_low_fps", "mean"),
    ).sort_values("avg_fps")

    fig = go.Figure()
    fig.add_trace(go.Bar(y=g.index, x=g["avg_fps"], name="Average", orientation="h",
                         marker_color="#3b82f6", text=g["avg_fps"].round(1),
                         textposition="outside"))
    fig.add_trace(go.Bar(y=g.index, x=g["low_1pct"], name="1% low", orientation="h",
                         marker_color="#f97316", text=g["low_1pct"].round(1),
                         textposition="outside"))
    fig.update_layout(barmode="group")
    fig.update_xaxes(range=[0, g.max().max() * 1.15])
    return style(fig, "FPS (higher is better)", None, height=340), g


# ---------------------------------------------------------------- quality plots
def quality_figs(df: pd.DataFrame) -> dict:
    psnr, ssim = df["PSNR (dB)"], df["SSIM"]
    figs = {}

    f = go.Figure(go.Scatter(x=df.index, y=psnr, mode="lines+markers", name="PSNR",
                             line_color="#3b82f6"))
    f.add_hline(y=psnr.mean(), line_dash="dash", line_color="#dc2626",
                annotation_text=f"mean {psnr.mean():.2f} dB")
    figs["PSNR per image"] = style(f, "Image index", "PSNR (dB)", 320)

    f = go.Figure(go.Scatter(x=df.index, y=ssim, mode="lines+markers", name="SSIM",
                             line_color="#16a34a"))
    f.add_hline(y=ssim.mean(), line_dash="dash", line_color="#dc2626",
                annotation_text=f"mean {ssim.mean():.4f}")
    figs["SSIM per image"] = style(f, "Image index", "SSIM", 320)

    f = go.Figure(go.Histogram(x=psnr.dropna(), nbinsx=20, marker_color="#3b82f6"))
    figs["PSNR distribution"] = style(f, "PSNR (dB)", "Count", 320)

    f = go.Figure(go.Scatter(x=psnr, y=ssim, mode="markers", name="image",
                             marker=dict(color="#8b5cf6", opacity=0.7, size=8)))
    figs["PSNR vs SSIM"] = style(f, "PSNR (dB)", "SSIM", 320)
    return figs


# ---------------------------------------------------------------- accuracy plots
def confusion_fig(tp, fp, tn, fn):
    cm = np.array([[tn, fp], [fn, tp]])
    text = [[f"<b>{v}</b><br>{v / cm.sum():.0%}" for v in row] for row in cm]

    fig = go.Figure(go.Heatmap(
        z=cm, x=["Verified Neg", "Verified Pos"], y=["Actual Neg", "Actual Pos"],
        text=text, texttemplate="%{text}", textfont=dict(size=18, color="#0f172a"),
        colorscale=[[0, "#f1f5f9"], [1, "#60a5fa"]], showscale=False, xgap=3, ygap=3,
        hovertemplate="Actual: %{y}<br>Verified: %{x}<br>Count: %{z}<extra></extra>",
    ))
    fig.update_yaxes(autorange="reversed")
    return style(fig, "Verified", "Actual", height=380)


# ---------------------------------------------------------------- UI
st.title("Skripsi Data Visualization")
tab_perf, tab_quality, tab_acc = st.tabs(["Performance", "Quality", "Accuracy"])

# ---------------------------------------------------------------- Performance
with tab_perf:
    # ---- overview
    with st.container(border=True):
        st.subheader("Benchmark summary")
        try:
            path, df_sum = read_latest(FPS_SUMMARY)
            fig, g = fps_summary_fig(df_sum)

            best = g["avg_fps"].idxmax()
            k1, k2, k3 = st.columns(3)
            k1.metric("Fastest config", best)
            k2.metric("Best average FPS", f"{g['avg_fps'].max():.1f}")
            k3.metric("Best 1% low FPS", f"{g['low_1pct'].max():.1f}")

            c1, c2 = st.columns([3, 2])
            c1.plotly_chart(fig, width="stretch", config=PLOT_CFG)
            c2.dataframe(
                g.sort_values("avg_fps", ascending=False),
                width="stretch",
                column_config={
                    "avg_fps": st.column_config.NumberColumn("Avg FPS", format="%.1f"),
                    "low_1pct": st.column_config.NumberColumn("1% low", format="%.1f"),
                },
            )
        except FileNotFoundError as e:
            st.warning(str(e))

    # ---- explorer
    with st.container(border=True):
        st.subheader("Run explorer")
        c1, c2 = st.columns([2, 1])
        label = c1.selectbox("Run type", list(FPS_SOURCES.keys()))
        window_s = c2.slider("Window size (s)", 0.1, 5.0, 0.5, 0.1,
                             help="Frames are averaged over this window to smooth the line.")

        try:
            files = list_csvs(FPS_SOURCES[label])
        except FileNotFoundError as e:
            st.warning(str(e))
            st.stop()

        fig_all, run_summary = fps_all_runs_fig(files, window_s)

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Runs", len(files))
        k2.metric("Mean avg FPS", f"{run_summary['avg_fps'].mean():.1f}")
        k3.metric("Mean 1% low", f"{run_summary['1%_low_fps'].mean():.1f}")
        k4.metric("Run-to-run std", f"{run_summary['avg_fps'].std():.2f}",
                  help="Standard deviation of avg FPS across runs. Lower = more consistent.")

        tab_all, tab_one = st.tabs(["All runs", "Single run"])

        with tab_all:
            st.plotly_chart(fig_all, width="stretch", config=PLOT_CFG)
            st.caption("Click a legend entry to hide a run. Double-click to isolate it.")
            with st.expander("Per-run stats"):
                st.dataframe(
                    run_summary, width="stretch",
                    column_config={
                        "avg_fps": st.column_config.ProgressColumn(
                            "Avg FPS", format="%.1f", min_value=0,
                            max_value=float(run_summary["avg_fps"].max() * 1.1)),
                        "1%_low_fps": st.column_config.NumberColumn("1% low", format="%.1f"),
                    },
                )
                st.download_button("Download stats CSV", run_summary.to_csv().encode(),
                                   file_name=f"{label.replace(' ', '_')}_run_stats.csv",
                                   mime="text/csv")

        with tab_one:
            chosen = st.selectbox(
                "Select run", files,
                format_func=lambda f: os.path.splitext(os.path.basename(f))[0],
                key=f"run_select_{label}",
            )
            df_run = load_csv(chosen, os.path.getmtime(chosen))
            fig_one, avg_fps, low_1pct = fps_single_run_fig(df_run, window_s)

            m1, m2, m3 = st.columns(3)
            m1.metric("Average FPS", f"{avg_fps:.1f}",
                      delta=f"{avg_fps - run_summary['avg_fps'].mean():+.1f} vs mean")
            m2.metric("1% low FPS", f"{low_1pct:.1f}",
                      delta=f"{low_1pct - run_summary['1%_low_fps'].mean():+.1f} vs mean")
            m3.metric("Frames", f"{len(df_run):,}")
            st.plotly_chart(fig_one, width="stretch", config=PLOT_CFG)

# ---------------------------------------------------------------- Quality
with tab_quality:
    try:
        path, df_q = read_latest(QUALITY)

        n_identical = int(np.isinf(df_q["PSNR (dB)"]).sum())
        df_clean = df_q.copy()
        df_clean["PSNR (dB)"] = df_clean["PSNR (dB)"].replace(np.inf, np.nan)

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Images", len(df_clean))
        k2.metric("Mean PSNR (dB)", f"{df_clean['PSNR (dB)'].mean():.2f}")
        k3.metric("Mean SSIM", f"{df_clean['SSIM'].mean():.4f}")
        k4.metric("Identical images", n_identical,
                  help="PSNR = ∞. These are excluded from PSNR charts and the mean.")

        figs = quality_figs(df_clean)
        titles = list(figs)
        for row in (titles[:2], titles[2:]):
            cols = st.columns(2)
            for col, title in zip(cols, row):
                with col.container(border=True):
                    st.markdown(f"**{title}**")
                    st.plotly_chart(figs[title], width="stretch", config=PLOT_CFG)

        with st.expander("Raw data"):
            st.dataframe(df_clean, width="stretch")
    except FileNotFoundError as e:
        st.warning(str(e))

# ---------------------------------------------------------------- Accuracy
with tab_acc:
    try:
        path, df_p = read_latest(PERFORMANCE)
        tp, fp, tn, fn = df_p.loc[0, ["tp", "fp", "tn", "fn"]]

        total = tp + fp + tn + fn
        accuracy = (tp + tn) / total if total else float("nan")
        precision = tp / (tp + fp) if (tp + fp) else float("nan")
        recall = tp / (tp + fn) if (tp + fn) else float("nan")
        f1 = (2 * precision * recall / (precision + recall)
              if precision == precision and recall == recall and (precision + recall)
              else float("nan"))

        left, right = st.columns([1, 1])
        with left:
            a, b = st.columns(2)
            a.metric("Accuracy", pct(accuracy))
            b.metric("F1", pct(f1))
            c, d = st.columns(2)
            c.metric("Precision", pct(precision), help="TP / (TP + FP)")
            d.metric("Recall", pct(recall), help="TP / (TP + FN)")
            st.caption(f"{int(total)} samples: TP {int(tp)} · FP {int(fp)} · "
                       f"TN {int(tn)} · FN {int(fn)}")
        with right:
            with st.container(border=True):
                st.plotly_chart(confusion_fig(tp, fp, tn, fn),
                                width="stretch", config=PLOT_CFG)
    except FileNotFoundError as e:
        st.warning(str(e))