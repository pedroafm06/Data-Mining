"""Reproduce the development-only A2 evaluation from the course source."""
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from kdd_revision.rubric_audit import run
from kdd_revision.rubric_bootstrap import bootstrap
from kdd_revision.schema import SOURCE_DEFAULT

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=SOURCE_DEFAULT)
    args = parser.parse_args()
    membership = bootstrap(ROOT, args.source)
    if membership['membership_sha256'] != '18d8474c9cabb4e1e24130c7e5fde1f66d013cf1ef45ca4b8e851cf62d20b299':
        raise RuntimeError('Reconstructed partition differs from the published reference.')
    print('Verified development partition:', membership['n_development'], flush=True)
    run(ROOT, args.source)
