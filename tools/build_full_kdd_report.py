"""Build integrated A2 report and detailed decisions from the current completed run."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from kdd_revision.full_report import generate
if __name__=='__main__':print(generate(ROOT).relative_to(ROOT))
