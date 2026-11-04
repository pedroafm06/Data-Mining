"""Portable inputs, clear failures and partition identity guards for the current A2 entrypoint."""
from pathlib import Path
import os,subprocess,sys
import pandas as pd
import pytest
from kdd_revision.preprocessing.run import validated_source,validated_partitions,run_preprocessing
from kdd_revision.schema import PROJECT_ROOT,SOURCE_DEFAULT,PARTITIONS_DEFAULT


def test_defaults_are_inside_the_repository():
    assert SOURCE_DEFAULT==PROJECT_ROOT/'dados/raw/UCMF_raw.csv'
    assert PARTITIONS_DEFAULT==PROJECT_ROOT/'config/particoes_referencia.csv'


def test_missing_source_is_clear_and_does_not_create_outputs(tmp_path):
    output=tmp_path/'outputs'
    with pytest.raises(FileNotFoundError,match='--source'):
        run_preprocessing(source=tmp_path/'missing.csv',output_dir=output)
    assert not output.exists()


def test_wrong_source_hash_is_rejected_before_outputs(tmp_path):
    source=tmp_path/'raw.csv';source.write_text('ID,Peso\n1,1\n');out=tmp_path/'outputs'
    with pytest.raises(ValueError,match='SHA-256 mismatch'):
        run_preprocessing(source=source,output_dir=out)
    assert not out.exists()


@pytest.mark.parametrize('rows,message',[
    ([['1','development'],['1','test']],'unique'),
    ([['1','development'],['2','holdout']],'development and test only'),
    ([['1','development'],['999','test']],'absent'),
    ([[' 1','development'],['2','test']],'exact'),
])
def test_bad_partition_memberships_are_not_silently_repaired(tmp_path,rows,message):
    p=tmp_path/'partitions.csv';pd.DataFrame(rows,columns=['ID','partition']).to_csv(p,index=False)
    with pytest.raises(ValueError,match=message):validated_partitions(p,pd.DataFrame({'ID':['1','2']}))


def test_explicit_partition_path_preserves_order_and_identity(tmp_path):
    p=tmp_path/'partitions.csv';expected=pd.DataFrame({'ID':['2','1'],'partition':['development','test']});expected.to_csv(p,index=False)
    resolved,observed=validated_partitions(p,pd.DataFrame({'ID':['1','2']}))
    assert resolved==p.resolve();pd.testing.assert_frame_equal(observed,expected)


def test_current_cli_reports_missing_source_without_a_traceback(tmp_path):
    script=PROJECT_ROOT/'tools/run_preprocessing.py'
    result=subprocess.run([sys.executable,str(script),'--source',str(tmp_path/'missing.csv')],capture_output=True,text=True)
    assert result.returncode==2 and 'Clinical CSV not found' in result.stderr
    assert 'Traceback' not in result.stderr
