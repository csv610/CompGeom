import importlib
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

for path in (ROOT, SRC):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


def test_core_package_imports():
    importlib.import_module("compgeom")
    importlib.import_module("compgeom.mesh")
    importlib.import_module("compgeom.mesh.surfmesh.surf_mesh_repair")


def test_engapp_modules_import_against_compgeom_package():
    importlib.import_module("engapp.cfd_analysis")
    importlib.import_module("engapp.molecular_geometry")
    importlib.import_module("engapp.robotics_geometry")
    importlib.import_module("engapp.topo_analysis")
