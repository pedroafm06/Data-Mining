"""Checks for exact identities and tolerance-bounded numerical reproduction."""

def compare_records(expected,actual,tolerance=1e-10):
    import math
    if expected['columns']!=actual['columns'] or len(expected['records'])!=len(actual['records']):
        raise AssertionError('Aggregate result schema or row count changed.')
    for i,(left,right) in enumerate(zip(expected['records'],actual['records'])):
        for key,a in left.items():
            b=right[key]
            if key in {'ID','scenario','candidate','candidate_group','partition','inner_fold','y','pred'}:
                if a != b: raise AssertionError(f'Identity/partition changed at row {i}, {key}: {a!r} -> {b!r}')
            elif isinstance(a,(int,float)) and not isinstance(a,bool) and isinstance(b,(int,float)):
                if not math.isclose(a,b,rel_tol=tolerance,abs_tol=tolerance):
                    raise AssertionError(f'Non-reproducible aggregate metric at row {i}, {key}: {a} -> {b}')
            elif a!=b:
                raise AssertionError(f'Non-reproducible aggregate value at row {i}, {key}: {a!r} -> {b!r}')

def compare_values(left,right,path='',tolerance=1e-10):
    import math
    if isinstance(left,dict):
        if not isinstance(right,dict) or set(left)!=set(right):raise AssertionError(f'Reference keys changed: {path}')
        for key in left:compare_values(left[key],right[key],path+'/'+str(key),tolerance)
    elif isinstance(left,list):
        if not isinstance(right,list) or len(left)!=len(right):raise AssertionError(f'Reference list changed: {path}')
        for i,(a,b) in enumerate(zip(left,right)):compare_values(a,b,path+'/'+str(i),tolerance)
    elif isinstance(left,(int,float)) and not isinstance(left,bool) and isinstance(right,(int,float)):
        if not math.isclose(left,right,rel_tol=tolerance,abs_tol=tolerance):raise AssertionError(f'Metric changed: {path}: {left}->{right}')
    elif left!=right:raise AssertionError(f'Reference changed: {path}: {left!r}->{right!r}')
