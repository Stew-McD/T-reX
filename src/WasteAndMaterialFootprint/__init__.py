import os
import sys
from pathlib import Path

# Add the config dir to the Python path
cwd = Path.cwd()
dir_config = cwd.parents[1] / 'config'
sys.path.insert(0, str(dir_config))