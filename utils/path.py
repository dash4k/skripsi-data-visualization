from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

FPS_NO_TAMPER_DETECTION = BASE_DIR / "fps" / "data" / "frames_no_tamper_detection_*.csv"
FPS_ANIMATION = BASE_DIR / "fps" / "data" / "frames_on_animation_changed_*.csv"
FPS_FRAME = BASE_DIR / "fps" / "data" / "frames_on_frame_changed_*.csv"
FPS_PROCESS = BASE_DIR / "fps" / "data" / "frames_on_process_*.csv"
FPS_SUMMARY = BASE_DIR / "fps" / "data" / "benchmark_summary.csv"
FPS_OUTPUTS = BASE_DIR / "fps" / "outputs"

QUALITY = BASE_DIR / "quality" / "data" / "results_*.csv"
QUALITY_OUTPUTS = BASE_DIR / "quality" / "outputs"

PERFORMANCE = BASE_DIR / "performance" / "data" / "results_*.csv"
PERFORMANCE_OUTPUTS = BASE_DIR / "performance" / "outputs"