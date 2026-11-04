from pathlib import Path
import argparse,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from kdd_revision.application import run_application
from kdd_revision.schema import SOURCE_DEFAULT
if __name__=='__main__':
    p=argparse.ArgumentParser(description='Reapply frozen A2 models with explicit input-coverage requirements')
    p.add_argument('--source',type=Path,default=SOURCE_DEFAULT);args=p.parse_args();run_application(ROOT,args.source)
