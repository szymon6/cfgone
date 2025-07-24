import sys
from .core import load_config

sys.modules[__name__] = load_config()
