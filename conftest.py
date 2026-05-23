import sys
from pathlib import Path

# Ensure the project root is on sys.path so `from app.x import y` works
# whether pytest is invoked as `pytest`, `python -m pytest`, or via CI.
sys.path.insert(0, str(Path(__file__).parent))
