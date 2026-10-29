"""Compatibility entry point. Build the shelf and all books together."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).resolve().parents[1] / 'build_library.py'), run_name='__main__')
