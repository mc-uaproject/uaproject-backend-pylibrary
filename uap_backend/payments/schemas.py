import importlib
import pkgutil
from pathlib import Path

PACKAGE_DIR = Path(__file__).parent

for _, module_name, _ in pkgutil.iter_modules([str(PACKAGE_DIR)]):
    try:
        importlib.import_module(f"payments.{module_name}.schemas")
    except ModuleNotFoundError:
        pass
