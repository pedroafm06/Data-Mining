#!/usr/bin/env python3
"""Apply A2 cleaning and transformations only; no predictive model is trained."""
import argparse
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from kdd_revision.schema import SOURCE_DEFAULT,PARTITIONS_DEFAULT,PROJECT_ROOT
from kdd_revision.preprocessing.run import run_preprocessing

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,default=SOURCE_DEFAULT,help='Clinical input CSV, excluded from version control')
    parser.add_argument('--partitions',type=Path,default=PARTITIONS_DEFAULT,help='Frozen development/test reference CSV')
    parser.add_argument('--output-dir',type=Path,default=None,help='Output directory (default: artifacts/a2_preprocessing)')
    args=parser.parse_args(argv)
    try:return run_preprocessing(root=PROJECT_ROOT,source=args.source,partitions=args.partitions,output_dir=args.output_dir)
    except (FileNotFoundError,ValueError) as error:parser.error(str(error))

if __name__=='__main__':main()
