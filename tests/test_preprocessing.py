from datetime import date
import importlib.util
from pathlib import Path
import joblib,numpy as np,pandas as pd,pytest
from kdd_revision.schema import ORIGINAL,SCENARIOS,NUMERIC
from kdd_revision.preprocessing.preparation import prepare_final,relative_age,calendar_age,model_frame
from kdd_revision.preprocessing.transformer import AppliedPreprocessor,MISSING,UNSEEN

def raw_example():
    rows=[]
    for i in range(4):
        r={c:'' for c in ORIGINAL};r.update(ID=str(i),Peso='12',Altura='90',IMC='14.8',Atendimento='15/08/05',DN='15/08/03',IDADE='2.07',SEXO='F',SOPRO='Ausente',PULSOS='Normais',B2='Normal',**{'NORMAL X ANORMAL':'Normal'})
        rows.append(r)
    return pd.DataFrame(rows)[ORIGINAL]

def frame():
    n=80;x=pd.DataFrame({'ID':[str(i) for i in range(n)]})
    for c in SCENARIOS['A']:
        x[c]=np.arange(n,dtype=float)+1 if c in NUMERIC else ['a','b']*(n//2)
    x['IDADE']=np.r_[np.full(40,.5),np.full(40,15.)]
    x['Altura']=np.r_[np.full(40,70.),np.full(40,170.)];x['Peso']=np.r_[np.full(40,8.),np.full(40,50.)]
    return x

def test_relative_age_without_forcing_century():
    r=relative_age('15/08/05','15/08/03')
    assert r['resolved'] and r['age']==2 and not r['absolute_dates_confirmed']
    assert r['n_compatible_pairs']==2
    p=prepare_final(raw_example());assert p.data.IDADE.eq(2).all();assert p.data.Atendimento.isna().all();assert p.data.DN.isna().all()

def test_twentieth_birthday_calendar_boundary():
    assert relative_age('28/02/2020','01/03/2000')['resolved']
    assert not relative_age('01/03/2020','01/03/2000')['resolved']
    assert calendar_age(date(2000,3,1),date(2020,3,1))==20

def test_zero_age_and_negative_raw_preserved():
    r=raw_example();r.loc[0,['Atendimento','DN','IDADE']]=['01/01/2005','01/01/2005','0'];r.loc[1,'IDADE']='-99'
    a=prepare_final(r);assert a.data.IDADE.iloc[0]==0
    assert a.data.meta_IDADE_original.iloc[1]==-99 and a.data.meta_IDADE_original_raw.iloc[1]=='-99'
    assert a.data.IDADE.iloc[1]==2

def test_bad_date_does_not_repair_century_by_guessing():
    r=relative_age('15/08/05','15/08/1980');assert not r['resolved']
    assert not relative_age('28/03/0/5','01/01/2001')['resolved']

def test_historical_bmi_not_deleted_when_parent_missing_without_joint_evidence():
    r=raw_example();r.loc[0,['Peso','IMC']]=['','17']
    a=prepare_final(r);safe=model_frame(a.data)
    assert np.isnan(safe.Peso.iloc[0]) and safe.IMC.iloc[0]==17
    assert a.data.flag_IMC_historical_with_unusable_parents.iloc[0]

def test_prepare_does_not_mutate_raw_or_remove_rows():
    r=raw_example();before=r.copy(deep=True);a=prepare_final(r)
    pd.testing.assert_frame_equal(r,before);assert a.data.ID.tolist()==r.ID.tolist()

def test_conditional_median_uses_observed_age_not_filled_age():
    x=frame();x.loc[0,'Altura']=np.nan;t=AppliedPreprocessor(min_count=20).fit(x)
    z=x.iloc[[0,50]].copy();z.loc[0,'IDADE']=np.nan;z.loc[0,'Altura']=np.nan
    out=t.transform(z)
    assert out.Altura.iloc[0]==t.medians_['Altura']
    assert out.Altura.iloc[1]==170
    young=z.iloc[[0]].copy();young['IDADE']=.5
    assert t.transform(young).Altura.iloc[0]==70

def test_reserved_missing_and_unknown_have_separate_onehot_and_binary():
    x=frame();x.loc[0,'SOPRO']=np.nan;t=AppliedPreprocessor().fit(x)
    a=x.iloc[[0,1]].copy();a.loc[1,'SOPRO']='new category';a.loc[0,'Peso']=np.nan
    for rep in ['units','standard','log_weight_standard']:
        z=t.transform(a,rep)
        binary=[d['name'] for d in t.column_dictionary_ if d['kind']!='continuous_measurement']
        assert set(np.unique(z[binary].to_numpy()))<={0,1}
        names=[d['name'] for d in t.column_dictionary_ if d.get('source')=='SOPRO']
        assert z[names].sum(axis=1).eq(1).all()
        miss=next(d['name'] for d in t.column_dictionary_ if d.get('source')=='SOPRO' and d.get('category')==MISSING)
        unseen=next(d['name'] for d in t.column_dictionary_ if d.get('source')=='SOPRO' and d.get('category')==UNSEEN)
        assert z[miss].iloc[0]==1 and z[unseen].iloc[1]==1

def test_fitted_parameters_cannot_learn_from_transformed_data_or_y():
    x=frame();t=AppliedPreprocessor().fit(x);before=t.metadata()
    q=x.iloc[:3].copy();q.Peso=100000.;q.SOPRO='future'
    t.transform(q);assert before==t.metadata()
    with pytest.raises(ValueError):AppliedPreprocessor().fit(x,np.zeros(len(x)))

def test_only_weight_log_and_indicators_are_not_scaled():
    x=frame();x.loc[0,'Peso']=np.nan;t=AppliedPreprocessor().fit(x)
    u=t.transform(x);s=t.transform(x,'standard');l=t.transform(x,'log_weight_standard')
    assert np.allclose(l.Altura,s.Altura)
    assert np.allclose(l.Peso,(np.log1p(u.Peso)-t.log_means_['Peso'])/t.log_scales_['Peso'])
    assert s.Peso__imputado.iloc[0]==l.Peso__imputado.iloc[0]==1

def test_all_missing_numeric_fit_has_no_silent_clinical_zero():
    x=frame();x.Altura=np.nan
    with pytest.raises(ValueError,match='No observed'):AppliedPreprocessor().fit(x)

def test_ids_targets_dates_are_not_predictors():
    x=frame()
    for c in ['ID','NORMAL X ANORMAL','DN','flag_x']:
        with pytest.raises(ValueError):AppliedPreprocessor(features=[c],age_group_columns=(),log_columns=()).fit(x)

def test_joblib_roundtrip_is_exact(tmp_path):
    x=frame();t=AppliedPreprocessor().fit(x);p=tmp_path/'t.joblib';joblib.dump(t,p);r=joblib.load(p)
    for rep in ['units','standard','log_weight_standard']:pd.testing.assert_frame_equal(t.transform(x,rep),r.transform(x,rep))

def test_real_applied_exports_match_saved_transformer():
    root=Path(__file__).resolve().parents[1];out=root/'artifacts/a2_preprocessing'
    if not (out/'transformador_preprocessamento.joblib').exists():pytest.skip('Run final A2 to validate its real exports')
    base=pd.read_csv(out/'base_para_transformacao.csv',dtype={'ID':str})
    mapping=pd.read_csv(out/'mapa_linhas.csv',dtype={'ID':str})
    semantic=pd.read_csv(out/'base_semantica.csv',dtype={'ID':str})
    transformer=joblib.load(out/'transformador_preprocessamento.joblib')
    assert len(base)==len(mapping)==len(semantic)==12873
    assert mapping.ID.tolist()==semantic.ID.tolist()==base.ID.tolist()
    assert mapping.partition.eq('development').sum()==transformer.n_fit_==9361
    assert mapping.partition.eq('test').sum()==2342
    for rep,name in [('units','matriz_unidades'),('standard','matriz_padronizada'),('log_weight_standard','matriz_log_peso_padronizada')]:
        export=pd.read_csv(out/(name+'.csv'));expected=transformer.transform(base,rep)
        assert list(export)==list(expected) and export.shape==expected.shape
        assert np.max(abs(export.to_numpy()-expected.to_numpy()))<=1e-10
        assert 'ID' not in export and 'NORMAL X ANORMAL' not in export
        binary=[d['name'] for d in transformer.column_dictionary_ if d['kind']!='continuous_measurement']
        assert set(np.unique(export[binary].to_numpy()))<={0,1}

def test_newly_recovered_age_updates_eligibility_and_summary():
    r=raw_example();r.loc[0,'IDADE']='-99'
    p=prepare_final(r)
    assert p.data.flag_IDADE_invalid_input.iloc[0]
    assert p.eligibility.motivo.iloc[0]=='incluido' and p.eligibility.idade_disponivel.iloc[0]
    assert p.summary['n_changes']==len(p.changes)
    assert p.summary['candidate_equivalence']['uses_corrected_age']

def test_out_of_cohort_absolute_dates_keep_alert_even_with_fallback():
    r=raw_example();r.loc[0,['DN','Atendimento','IDADE']]=['01/01/1900','01/01/2000','5']
    p=prepare_final(r)
    assert p.data.flag_age_calculated_outside_cohort.iloc[0]
    assert p.data.meta_IDADE_absolute_calculated.iloc[0]==100
    assert p.data.IDADE.iloc[0]==5
    assert p.data.meta_IDADE_source.iloc[0]=='original_numeric_unverified_fallback'
    assert p.data.flag_age_conflict_gt1year.iloc[0]

def test_real_quarantine_excludes_crossing_candidate_before_fit():
    root=Path(__file__).resolve().parents[1];out=root/'artifacts/a2_preprocessing'
    if not (out/'particoes_ajuste.csv').exists():pytest.skip('Run final A2 for partition artifact verification')
    mapping=pd.read_csv(out/'particoes_ajuste.csv',dtype={'ID':str})
    frozen=pd.read_csv(root/'config/particoes_referencia.csv',dtype={'ID':str})
    assert mapping.partition.eq('quarentena_equivalencia').sum()==1
    assert set(mapping.loc[mapping.partition.eq('test'),'ID'])==set(frozen.loc[frozen.partition.eq('test'),'ID'])
    tr=joblib.load(out/'transformador_preprocessamento.joblib')
    assert tr.n_fit_==9361
    base=pd.read_csv(out/'base_para_transformacao.csv',dtype={'ID':str})
    sig=pd.util.hash_pandas_object(base[SCENARIOS['A']],index=False)
    ok=base[SCENARIOS['A']].notna().sum(axis=1).ge(8)
    assert not(set(sig[ok&mapping.partition.eq('development')])&set(sig[ok&mapping.partition.eq('test')]))

def test_reviewed_policy_preserves_possible_extremes_and_arithmetic_observed_bmi():
    r=raw_example();r.loc[0,['Peso','Altura','IDADE','Atendimento','DN','IMC','FC']]=['1.2','36','0.04','15/01/2005','01/01/2005','','300']
    r.loc[1,['Peso','Altura','IDADE','Atendimento','DN','FC']]=['157','150','13','','','230']
    p=prepare_final(r);reviewed=model_frame(p.data);legacy=model_frame(p.data,'historical')
    assert reviewed.Altura.iloc[0]==36 and reviewed.FC.iloc[0]==300
    assert reviewed.Peso.iloc[1]==157 and reviewed.FC.iloc[1]==230
    assert np.isclose(reviewed.IMC.iloc[0],1.2/.36**2)
    assert p.data.meta_IMC_source.iloc[0]=='arithmetic_observed_parents_reviewed'
    assert np.isnan(legacy.Altura.iloc[0]) and np.isnan(legacy.FC.iloc[0])

def test_low_positive_fc_pad_and_arithmetic_bmi_are_not_errors_by_threshold():
    r=raw_example();r.loc[0,['Peso','Altura','IMC','FC','PA SISTOLICA','PA DIASTOLICA']]=['127','123','','10','90','6']
    p=prepare_final(r);safe=model_frame(p.data)
    assert safe.FC.iloc[0]==10 and safe['PA DIASTOLICA'].iloc[0]==6
    assert np.isclose(safe.IMC.iloc[0],127/1.23**2) and safe.IMC.iloc[0]>60
    assert p.data.flag_FC_suspect_envelope.iloc[0] and p.data.flag_IMC_suspect_envelope.iloc[0]

def test_gross_fc_curation_is_flagged_not_digit_repair():
    r=raw_example();r.loc[0,'FC']='9288';p=prepare_final(r);safe=model_frame(p.data)
    assert p.data.FC.iloc[0]==9288 and np.isnan(safe.FC.iloc[0])
    assert model_frame(p.data,'preserve_suspect').FC.iloc[0]==9288

def test_final_status_separates_recovered_age_bmi_from_raw_invalid_missing():
    r=raw_example();r.loc[0,'IDADE']='-99';r.loc[0,'IMC']=''
    p=prepare_final(r)
    assert p.data.meta_IDADE_raw_status.iloc[0]=='invalid'
    assert p.data.meta_IDADE_status.iloc[0]=='derived_relative'
    assert p.data.meta_IMC_raw_status.iloc[0]=='missing'
    assert p.data.meta_IMC_status.iloc[0]=='derived_observed_parents'
    predictors=[c for c in ORIGINAL if c not in ['ID','NORMAL X ANORMAL']]
    assert p.groups.n_informative_fields.tolist()==p.data[predictors].notna().sum(axis=1).tolist()

def test_joint_anthropometric_curation_masks_parents_without_blame_or_age_deletion():
    r=raw_example();r.loc[0,['Peso','Altura','IMC']]=['157','46','742'];r.loc[1,['Peso','Altura','IMC']]=['47','53','167.3']
    p=prepare_final(r);safe=model_frame(p.data);keep=model_frame(p.data,'preserve_suspect')
    for i in [0,1]:
        assert p.data.flag_anthropometric_pair_extreme_ratio.iloc[i]
        assert p.data.IDADE.iloc[i]==safe.IDADE.iloc[i]==2
        assert safe[['Peso','Altura','IMC']].iloc[i].isna().all()
        assert p.data[['Peso','Altura','IMC']].iloc[i].notna().all()
        assert keep[['Peso','Altura','IMC']].iloc[i].notna().all()
        assert pd.isna(p.data.meta_IMC_calculated_reviewed.iloc[i])
        assert p.data.meta_IMC_source.iloc[i]=='original_historical'

def test_joint_guard_preserves_high_positive_bmi_below_broad_curation_ceiling():
    r=raw_example();r.loc[0,['Peso','Altura','IMC']]=['127','123',''];p=prepare_final(r);safe=model_frame(p.data)
    assert not p.data.flag_anthropometric_pair_extreme_ratio.iloc[0]
    assert np.isclose(safe.IMC.iloc[0],127/1.23**2)
    assert safe.Peso.iloc[0]==127 and safe.Altura.iloc[0]==123

def test_historical_bmi_inside_guard_cannot_bypass_known_joint_contradiction():
    r=raw_example();r.loc[0,['Peso','Altura','IMC']]=['11','33','99']
    p=prepare_final(r);safe=model_frame(p.data)
    assert p.data.flag_anthropometric_pair_extreme_ratio.iloc[0]
    assert p.data.IMC.iloc[0]==99
    assert safe[['Peso','Altura','IMC']].iloc[0].isna().all()
    assert p.data.IDADE.iloc[0]==safe.IDADE.iloc[0]==2

def test_partition_targets_and_ids_are_aligned_with_the_applied_matrices():
    root=Path(__file__).resolve().parents[1];out=root/'artifacts/a2_preprocessing'
    if not (out/'y_development.csv').exists():pytest.skip('Run final A2 for target sidecars')
    mapping=pd.read_csv(out/'mapa_linhas.csv',dtype={'ID':str})
    for partition in ['development','test','quarentena_equivalencia']:
        expected=mapping.loc[mapping.partition.eq(partition)]
        ids=pd.read_csv(out/('ids_'+partition+'.csv'),dtype={'ID':str})
        y=pd.read_csv(out/('y_'+partition+'.csv'))
        matrix=pd.read_csv(out/('matriz_unidades_'+partition+'.csv'))
        assert len(ids)==len(y)==len(matrix)==len(expected)
        assert ids.ID.tolist()==expected.ID.tolist()
        assert y.y.tolist()==expected.y.tolist()
        assert list(y)==['y'] and set(y.y)<={0,1}
