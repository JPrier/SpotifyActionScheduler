import pathlib
import sys

# 1) Compute path to your src folder:
ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "spotifyActionService" / "src"

# 2) Prepend it to sys.path so "import spotifyActionService" works everywhere
sys.path.insert(0, str(SRC.resolve()))
