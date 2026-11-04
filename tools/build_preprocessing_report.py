#!/usr/bin/env python3
"""Generate the A2 preprocessing report, without training predictive models."""
from pathlib import Path
import argparse
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from kdd_revision.preprocessing_report import generate

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,help='CSV original; alternativa: KDD_SOURCE ou dados/raw/UCMF_raw.csv')
    parser.add_argument('--artifacts',type=Path,help='Pasta das saídas do pré-processamento')
    args=parser.parse_args()
    print(generate(ROOT,source=args.source,artifact_dir=args.artifacts).relative_to(ROOT))

if __name__=='__main__':main()
