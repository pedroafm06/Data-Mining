"""Run the current A2 KDD process; keeps the submitted A1 unchanged."""
from pathlib import Path
import argparse,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from kdd_revision.schema import SOURCE_DEFAULT
from kdd_revision.preprocessing.run import run_preprocessing
from kdd_revision.preprocessing_report import generate
from kdd_revision.full_kdd import run_mining

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,default=SOURCE_DEFAULT)
    p.add_argument('--reuse-mining',action='store_true',help='Verify and reuse the completed frozen search; rerun current application and reporting')
    p.add_argument('--skip-preparation',action='store_true',help='Use already verified local preparation; source is still checked')
    args=p.parse_args()
    if not args.skip_preparation:run_preprocessing(ROOT,source=args.source);generate(ROOT,source=args.source)
    if args.reuse_mining:
        from kdd_revision.reproduction import verify_saved_run
        verify_saved_run(ROOT,source=args.source)
    else:
        run_mining(ROOT,source=args.source)
        from kdd_revision.reproduction import verify_saved_run
        verify_saved_run(ROOT,source=args.source)
    from kdd_revision.application import run_application
    run_application(ROOT,source=args.source)
    # Reporting remains a separate pure consumer of aggregate results.
    report=ROOT/'tools/build_full_kdd_report.py'
    if report.exists():
        import subprocess
        subprocess.run([sys.executable,str(report)],cwd=ROOT,check=True)
if __name__=='__main__':main()
