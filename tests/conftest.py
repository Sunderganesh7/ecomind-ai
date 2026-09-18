"""Deterministic test-environment settings.

The repository's embedding tests exercise the cached production
``all-MiniLM-L6-v2`` model.  Prevent Hugging Face from performing a network
metadata check during those unit tests; this neither replaces the model nor
changes application runtime behaviour.
"""

import os
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
backend_dir = root / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
