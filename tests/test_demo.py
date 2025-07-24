import sys
import os

# Add the parent directory to Python path so we can import cfgone
parent_dir = os.path.dirname(os.path.dirname(__file__))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import cfgone as cfg
print("=== Testing cfgone printing ===")
print()

print("cfgone")
print(cfg)
print()


print("=== Direct attribute access ===")
print(f"App name: {cfg.app.name}")
print(f"App debug: {cfg.app.debug}")
print(f"Database host: {cfg.database.host}")
print()
