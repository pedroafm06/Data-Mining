from kdd_revision.full_kdd import protocol
from kdd_revision.mining import candidates


def test_protocol_records_every_search_configuration_and_nested_design():
    p=protocol()
    assert p['candidate_count']==len(p['candidates'])==81
    assert p['candidates']==candidates()
    assert p['development_cv']['n_splits']==5
    assert p['nested_cv']['outer_folds']==p['nested_cv']['inner_folds']==3
    assert p['threshold']==.5
    assert len([c for c in candidates() if c['kind']=='tree'])==40
    assert len([c for c in candidates() if c['kind']=='logistic'])==32
    assert len([c for c in candidates() if c['kind']=='forest'])==8
