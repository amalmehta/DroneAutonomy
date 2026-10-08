"""Shared setup for idea experiments: import the project read-only, single-threaded torch."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
import os
os.chdir(ROOT)  # the project's code resolves runs/ and website/ relative to its root

import torch  # noqa: E402

torch.set_num_threads(1)


def save(path, obj):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(obj, indent=1))
