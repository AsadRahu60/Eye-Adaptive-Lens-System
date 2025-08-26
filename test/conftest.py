# test/conftest.py
import sys
import pathlib

# add repo root to import path (so 'host.pi.*' works locally like on CI)
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
