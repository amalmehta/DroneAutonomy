"""Regenerate every value, table and figure for one venue folder: python3 make_all.py <venue-dir>."""
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = ["make_values.py", "task_table.py", "tracking_table.py", "navigation_table.py", "step_size_table.py",
           "adaptation_curves.py", "example_flights.py"]


def main():
    venue_dir = Path(sys.argv[1] if len(sys.argv) > 1 else HERE.parent / "ieee-conf").resolve()
    env = dict(os.environ, VENUE_DIR=str(venue_dir), VENUE=os.environ.get("VENUE", "ieee"),
               SOURCE_DATE_EPOCH="1791244800", MPLBACKEND="Agg")
    (venue_dir / "figures").mkdir(parents=True, exist_ok=True)
    for s in SCRIPTS:
        subprocess.run([sys.executable, str(HERE / s)], check=True, env=env, cwd=HERE)
    print("regenerated", len(SCRIPTS), "outputs in", venue_dir)


if __name__ == "__main__":
    main()
